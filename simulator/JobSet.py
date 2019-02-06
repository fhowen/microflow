import Constants
from Flow import Flow
from Compu import Compu
from Reducer import Reducer
from Job import Job
import networkx as nx
import random
import os

class JobSet:
    def __init__(self):
        self.jobsList = []
    
    def addJob(self, submit_time, mapper_list, reducer_list, data_size_list):
        j = Job()
        j.set_attributes(submit_time, mapper_list, reducer_list, data_size_list)
        self.jobsList.append(j)

    # shuffle the flows to make a sender may has multiple metaflows
    def shuffleFlows(self, option):
        # define how to shuffle
        random_shuffle = 0
        base_dir = os.getcwd()
        file_name = os.path.join(base_dir, 'dags', "shuffle.txt")
        # randomly shuffle the flows
        if option == 0:
            f_open = open(file_name, 'w')
            for j in self.jobsList:
                # type 1 : random shuffle
                if random_shuffle == 1:
                    for r in j.reducerList:
                        m_list = r.mapperList
                        random.shuffle(m_list)
                        for i in range(0, len(r.flowList)):
                            r.flowList[i].srcID = m_list[i] 
                            f_open.write(str(r.flowList[i].srcID)+' ')
                        f_open.write("\n")
                # type 2 : one by one shift
                elif random_shuffle == 0:
                    cursor = 0
                    for r in j.reducerList:
                        m_list = r.mapperList
                        for i in range(0, len(r.flowList)):
                            r.flowList[i].srcID = m_list[(i + cursor)%len(m_list)]
                            f_open.write(str(r.flowList[i].srcID)+' ')
                        f_open.write("\n")
                        cursor += 1
            f_open.close()
        # read shuffle result from log
        elif option == 1:
            f_open = open(file_name, 'r')
            for j in self.jobsList:
                for r in j.reducerList:
                    line = f_open.readline().strip()
                    sp_line = line.split(' ')
                    print(sp_line)
                    for i in range(0, len(r.flowList)):
                        r.flowList[i].srcID = int(sp_line[i])
            f_open.close()
        

    # read coflow trace and add jobs
    def readTrace(self):
        base_dir = os.getcwd()
        f_name = os.path.join(base_dir, '', "coflow_trace_test.txt")
        f = open(f_name, 'r')
        print("Begin to read coflow_trace...")
        for line in f:
            line = line.strip()
            sp_line = line.split(' ')
            submit_time = int(sp_line[1])
            mapper_num = int(sp_line[2])
            cursor = 3 
            mapper_list = []
            for j in range(0, mapper_num):
                mapper_list.append(int(sp_line[cursor]))
                cursor += 1
            reducer_num = int(sp_line[cursor])
            cursor += 1
            reducer_list = []
            data_size_list = []
            #dealing each reducer
            for j in range(0, reducer_num):
                ssp_line = sp_line[cursor].split(':')
                reducer_id = int(ssp_line[0])
                data_size = float(ssp_line[1])*8*1024*1024
                reducer_list.append(reducer_id)
                data_size_list.append(data_size)
                cursor += 1
            self.addJob(submit_time, mapper_list, reducer_list, data_size_list)
        f.close()
    '''
    #set  alpha, bebta
    def dagAttrs(self, job, dag_type):
        mapper_num = len(job.mapperList)
        compu_num = job.dag.number_of_nodes() - mapper_num
        #1 set alpha and beta
        if dag_type == Constants.DNNDAG:
            for i in range(0, mapper_num):
                # set alpha
                job.dag.node[i]['alpha'] = mapper_num - i
        elif dag_type == Constants.WEBDAG:
            pass
        # TO DO ====
        elif dag_type == Constants.RANDOMDAG:
            job.dag.add_node("End_node")
            for i in range(mapper_num, mapper_num + compu_num + 1):
                job.dag.add_edge(i, "End_node")
            for i in range(0, mapper_num):
                p_list = nx.all_simple_paths(job.dag, source=i, target="End_node")
                max_rank = 0
                for j in p_list:
                    if len(j)>max_rank:
                        max_rank = len(j)
                job.dag.node[i]['alpha'] = max_rank - 1
            for i in range(mapper_num, mapper_num + compu_num + 1):
                job.dag.remove_edge(i, "End_node")
            job.dag.remove_node("End_node")
        else:
            pass
    '''

    #create the uniform dag for one job
    def createOneDag(self, dag_type, mapper_num):
        dag = nx.DiGraph()
        compu_num = 0
        if dag_type == Constants.DNNDAG:
            compu_num = mapper_num
            # create nodes, flow nodes followed by compu nodes
            for i in range(0, mapper_num):
                dag.add_node(i)
            for i in range(mapper_num, 2*mapper_num):
                dag.add_node(i)
            # add edges
            # 1. edges from flow to compu
            for i in range(0, mapper_num):
                dag.add_edge(i, i+mapper_num)
            # 2. edges from compu to compu
            for i in range(mapper_num, 2*mapper_num - 1):
                dag.add_edge(i, i+1)
            #print(dag.edges())
        elif dag_type == Constants.WEBDAG:
            compu_num = 1
            # mapper_num flow and 1 compu
            for i in range(0, mapper_num + 1):
                dag.add_node(i)
            # add edges
            for i in range(0, mapper_num):
                dag.add_edge(i, mapper_num)
        # random dag
        elif dag_type == Constants.RANDOMDAG:
            proba = 0.05
            nodes_matrix = []
            temp = []
            node_rank = 0
            # mapper num flow 
            for i in range(0, mapper_num):
                temp.append(i)
                dag.add_node(i)
            # add to matrix    
            node_rank += mapper_num
            nodes_matrix.append(temp)
            temp = []
            # compu nodes
            layer_num = random.randint(3, 10)
            # for each layer
            for i in range(1, layer_num + 1):
                # root layer
                if i == 1:
                    nodes_num = random.randint(1, mapper_num)
                # not root layer
                else:
                    nodes_num = random.randint(1, mapper_num)
                # add nodes
                compu_num += nodes_num
                for j in range(node_rank, node_rank + nodes_num):
                    temp.append(j)
                    dag.add_node(j)
                # forward and reset
                nodes_matrix.append(temp)
                node_rank += nodes_num
                temp = []
                # add edges
                #1 add edges for root layer
                if i == 1:
                    for j in nodes_matrix[0]:
                        dag.add_edge(j, j%len(nodes_matrix[1]) + mapper_num)
                #2 add edges for each layer, not root layer
                if i > 1:
                    b_cur = mapper_num
                    f_cur = nodes_matrix[i][0] - 1
                    # for each node in this layer, if not root layer
                    for j in nodes_matrix[i]:
                        # for each nodes in previous layer, only root layer can connect with flows
                        for k in range(b_cur, f_cur + 1):
                            if random.uniform(0, 1) < proba:
                                dag.add_edge(k, j)
                        # check in case no edge is added
                        if (len(dag.pred[j]) == 0):
                            # random choose a node as father
                            father_node = random.randint(b_cur, f_cur)
                            dag.add_edge(father_node, j)
        # dag for tasks with hard barriers
        elif dag_type == Constants.HARDDAG:
            # one compunum
            compu_num = 1
            for i in range(0, mapper_num + 1):
                dag.add_node(i)
            for i in range(0, mapper_num):
                dag.add_edge(i, mapper_num)
        else:
            pass
        return dag, compu_num
            

    #copy the relationship in pure dag to real dag of reducer
    def copyDag(self, pure_dag, reducer, dag_type):
        # generate flow tasks and compu tasks
        compu_num = pure_dag.number_of_nodes() - len(reducer.mapperList)
        reducer.dagType = dag_type
        # copy edges 
        for u,v in pure_dag.edges():
            #print(u,v)
            v = v - reducer.mapperNum
            # 1 flow --> compu
            if u < reducer.mapperNum:
                reducer.dag.add_edge(reducer.flowList[u], \
                                     reducer.compuList[v])
                # set metaflow tag
                reducer.flowList[u].metaflowTag = v
            # 2 compu --> compu 
            else:
                u = u - reducer.mapperNum
                reducer.dag.add_edge(reducer.compuList[u], \
                                     reducer.compuList[v])
        # init the neededFlow list in compu task
        for j in range(len(reducer.compuList)):
            for i in range(len(reducer.flowList)):
                if nx.has_path(reducer.dag, reducer.flowList[i], reducer.compuList[j]):
                    reducer.compuList[j].neededFlow.append(i)

    # === TO DO ====== where to assign the compute size ?
    # generate dag relationship and task size
    def genDags(self, dag_option):
        for j in self.jobsList:
            if dag_option == 0:
                #1--- generate a dag
                #dag_type = Constants.DNNDAG
                #dag_type = Constants.WEBDAG
                #dag_type = Constants.RANDOMDAG
                random_point = random.random()
                if random_point < Constants.HARD_RATIO:
                    dag_type = Constants.HARDDAG
                else:
                    dag_type = Constants.DNNDAG
                j.dagType = dag_type
                j.dag, compu_num = self.createOneDag(dag_type, len(j.mapperList))
                j.dag2Txt()
            elif dag_option == 1:
                #2--- read a dag
                dag_type, compu_num = j.txt2Dag()
                j.dagType = dag_type
            else:
                pass
            for r in j.reducerList:
                # assign the dag to each reducer
                r.genTasks(compu_num)
                self.copyDag(j.dag, r, dag_type)
                r.copyDagAttrs(dag_type)
                if (dag_option ==0):
                    r.dagSize()
            if dag_option == 0:
                j.storeSize()
            if dag_option == 1:
                j.readSize()
            # about shuffle 
            if dag_option == 0:
                self.shuffleFlows(0)
            if dag_option == 1:
                self.shuffleFlows(1)

    # store dag to .dot and .txt file
    def storeDag(self):
        for j in self.jobsList:
                j.dag2Dot()
                #r.dag2Txt()

    # read dag from txt file
    def readDag(self):
        for j in self.jobsList:
            for r in j.reducerList:
                r.txt2Dag()
                r.initAlphaBeta()



