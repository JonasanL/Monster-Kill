#
#                             _ooOoo_
#                            o8888888o
#                            88" . "88
#                            (| -_- |)
#                            O\  =  /O
#                         ____/`---'\____
#                       .'  \\|     |//  `.
#                      /  \\|||  :  |||//  \
#                     /  _||||| -:- |||||-  \
#                     |   | \\\  -  /// |   |
#                     | \_|  ''\---/''  |   |
#                     \  .-\__  `-`  ___/-. /
#                   ___`. .'  /--.--\  `. . __
#                ."" '<  `.___\_<|>_/___.'  >'"".
#               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#               \  \ `-.   \_ __\ /__ _/   .-` /  /
#          ======`-.____`-.___\_____/___.-`____.-'======
#                             `=---='
#          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                     佛祖保佑        永无BUG
#

import json
import time
from collections import defaultdict, deque
import random
import sys
import math
import utils
#1bow, 2wood, 3stone, 4iron, 5 gold,6 diamond
#[0] attact cost [1] max attack
rewards_map = {'swap_1':[-2,30],'swap_2':[-1,16],'swap_3':[-1,22],'swap_4':[-3.22,27],'swap_5':[-5.63,10],'swap_6':[-6.83,43],'go_back':[0,0],'go_front':[0,0]}

weapon_count_map = {'swap_1':0,'swap_2':0,'swap_3':0,'swap_4':0,'swap_5':0,'swap_6':0,'go_back':0,'go_front':0}

enemies = set(['WitherSkeleton','Stray','Husk','Giant','Spider','Zombie','Skeleton'
               ,'PigZombie','WitherBoss','VillagerGolem','Guardian','Witch','EnderDragon','Blaze','Ghast','Creeper','VindicationIllager','ZombieVillager','ElderGuardian'])

class Agent:
    # construct Agent object

    def __init__ (self, alpha=0.3, gamma=1, epsilon=0.5, n=1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.n = n
        self.weapon = 1
        self.q_table = dict()
        self.MonsterHeart = 20
        self.Heart = 20
        self.action = 0


        self.pastActions = []
    
    # get observations from world state, returns a world state dictionary
    @staticmethod
    def getObservations (world_state) -> dict:
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            return json.loads(msg)
        else:
            return dict()
    
    # get the position between agent and the clostest mob.
    # currently only considers zpos
    def getMobDistance (self, zpos, entities):
        distList = list()
        for mob in entities:
            if mob['name'] in enemies:
                distList.append(mob['z'] - zpos)
        if len(distList) > 0:
            return min(distList)
        else:
            return -100000

    # get current state with observation
    def getState (self, observations):
        floatDistance = self.getMobDistance(observations['ZPos'], observations['entities'])
        
        if floatDistance == -100000:
            return (floatDistance,1)
        
        if floatDistance > 15:
            floatDistance = 20
        elif floatDistance > 10:
            floatDistance = 15
        elif floatDistance > 5:
            floatDistance = 10
        
        
        
        return (int(abs(floatDistance)),1)
        
        if floatDistance == -100000:
            intDistance = -100000
        elif floatDistance < 0:
            intDistance = -1
        elif floatDistance <= 3:
            intDistance = 3
        elif floatDistance <= 5:
            intDistance = 5
        elif floatDistance <= 10:
            intDistance = 10
        elif floatDistance <= 15:
            intDistance = 15
        else:
            intDistance = 20
      #state = list((intDistance, self.weapon))
            #for i in self.pastActions:
            #state.append(i)
#return tuple(state)
        return intDistance,
    
    # get all possible actions with current state
    def getActions (self, state):
        
        actionList = ['go_back']

        actionList.append('go_front')
        for wid in range(1,7):
            actionList.append('swap_' + str(wid))

        return actionList
        
        
        
        if state[1] == 1:
            actionList.append("shot_0.4")
            actionList.append("shot_0.6")
            actionList.append("shot_0.9")
        

        return actionList

    # let agent host do action
    def act (self, action, agent_host):
        self.action+=1
        if action == 'go_front':
            agent_host.sendCommand('move 1')
            time.sleep(0.25)
            agent_host.sendCommand('move 0')
        elif action == 'go_back':
            agent_host.sendCommand('move -1')
            time.sleep(0.25)
            agent_host.sendCommand('move 0')
            #elif action == 'attack':
            #self.closeAttack(agent_host)
        elif action.startswith('swap'):
            weapon_count_map[action]+=1
            if int(action[5:]) != 1:
                self.swapWeapon(int(action[5:]), agent_host)

                self.closeAttack(agent_host)
            else:
                self.swapWeapon(1, agent_host)

                self.rangeShoot(0.6, agent_host)
#elif action.startswith('shot'):
# self.rangeShoot(float(action[5:]), agent_host)

        
    # swap to other weapons in hotbar, with weapon slot id
    def swapWeapon (self, id, agent_host):
        assert id >= 1, "Weapon ID out of range"
        assert id <= 6, "Weapon ID out of range"
        agent_host.sendCommand("hotbar.%s 1" % id)
        agent_host.sendCommand("hotbar.%s 0" % id)
        self.weapon = id

    # agent close attack. most possessing a sword
    def closeAttack (self, agent_host):
        assert self.weapon >= 1 and self.weapon <= 6, "Wrong close attack weapon"
        agent_host.sendCommand("attack 1")
        time.sleep(0.1)
        agent_host.sendCommand("attack 0")
    
    # agent range shot with given time
    def rangeShoot (self, floatTime, agent_host):
        assert self.weapon == 1, "Wrong range attack weapon"
        agent_host.sendCommand("use 1")
        time.sleep(floatTime)
        agent_host.sendCommand("use 0")
        
    def update_q_table(self, tau, S, A, R, T):
        """Performs relevant updates for state tau.
            
            Args
            tau: <int>  state index to update
            S:   <dequqe>   states queue
            A:   <dequqe>   actions queue
            R:   <dequqe>   rewards queue
            T:   <int>      terminating state index
            """

        curr_s, curr_a, curr_r = S.popleft(), A.popleft(), R.popleft()
        
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[S[-1]][A[-1]]

        old_q = self.q_table[curr_s][curr_a]
        self.q_table[curr_s][curr_a] = old_q + self.alpha * (G - old_q)

    
        # agent choose actions among possible_action list
    def choose_actions(self,curr_state, possible_actions, eps):
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0

        rnd = random.random()
        if rnd <= eps:
            action = random.randint(0, len(possible_actions)-1)
        else:
            sortedlist = [(k, self.q_table[curr_state][k]) for k in sorted(self.q_table[curr_state], key = self.q_table[curr_state].get, reverse = True)]
            if (len(sortedlist)) >= 2 and sortedlist[0][1] == sortedlist[1][1]:
                action = random.randint(0, len(possible_actions) - 1)
            else:
                a = sortedlist[0][0]
                for i in range(len(possible_actions)):
                    if a == possible_actions[i]:
                        action = i
                        break
        return possible_actions[action]

        
        
    def faceEnemy(self,observations,agent_host):
        for mob in observations['entities']:
            if mob['name'] == 'Zombie':
                zomx = float(mob['x'])
                zomy = float(mob['y'])
                zomz = float(mob['z'])
            if mob['name'] == 'Monster Killer':
                agentx = float(mob['x'])
                agenty = float(mob['y'])
                agentz = float(mob['z'])

        newx = agentx - zomx
        newz = agentz - zomz

        dis = self.getMobDistance(observations['ZPos'], observations['entities'])
        c = newx/dis

        #c = math.sqrt(math.pow(newx,2) + math.pow(newz,2))
        A = math.acos(c)
        angle = A * 180/3.1415926

    
    
    def damagedone(self,agent_host,observations,action):
        if action == 'go_back' or action == 'go_front':
            return 0
        
        damage = rewards_map[action][0]
        life =1000000
        for mob in observations['entities']:
            if mob['name'] == 'Zombie':
                life = mob['life']
        
        if life < self.MonsterHeart:
            damage += (self.MonsterHeart - life)
            self.MonsterHeart = life
            return damage*3



        
        return damage

    def receiveDamage(self,agent_host,observations):
        total = 0
        for mob in observations['entities']:
            if mob['name'] == 'Monster Killer':
                life = mob['life']

        if life < self.Heart:
            total = self.Heart-life
            self.Heart = life

        return total*-4
            
            
    def maxAttack(self,agent_host,observations,action):
        if rewards_map[action][1] == 0:
            return 0
        
        if weapon_count_map[action] > rewards_map[action][1]:
            return -20
        return 0
    
    def timedeclay(self):
        reward = math.exp(0.125*self.action) -1
        return -reward
    
    def rewardCalculate(self,agent_host,observations,action):
        total = -0.5
        
        
        
        total += self.damagedone(agent_host,observations,action)
        total += self.receiveDamage(agent_host,observations)
        total += self.maxAttack(agent_host,observations,action)
        #total += self.timedeclay()
        return total
        
    def change_direction(self,agent_host,observations):
        zx = 0
        zz = 0
        ax = 0
        az = 0
        for mob in observations['entities']:
            if mob['name'] != 'Monster Killer':
                zx = mob['x']
                zz = mob['z']
            elif mob['name'] == 'Monster Killer':
                ax = mob['x']
                az = mob['z']
        utils.turnFacingByAgentTargetPosition (ax, az, zx, zz, agent_host)
                

        
    def run(self,agent_host):
        for action in weapon_count_map:
            weapon_count_map[action] = 0


        deadflag = 0
        S, A, R = deque(), deque(), deque()
        present_reward = 0
        done_update = False
        while not done_update:
            world_state = agent_host.getWorldState()
            observations = self.getObservations(world_state)

            while len(observations) <= 1:
                observations = self.getObservations(world_state)

            s0 = self.getState(observations)
            possible_actions = self.getActions(s0)
            a0 = self.choose_actions(s0, possible_actions, self.epsilon)
            self.pastActions.append(a0)
            S.append(s0)
            A.append(a0)
            R.append(0)
            T = sys.maxsize
            for t in range(sys.maxsize):
                
                if t < T:
                    self.change_direction(agent_host,observations)
                    self.act(A[-1],agent_host)
                    if A[-1][0] == 's':
                        time.sleep(0.7)
                    world_state = agent_host.getWorldState()
                    for mob in observations['entities']:
                        if mob['name'] == 'Monster Killer':
                            life = mob['life']
                    self.Heart = life
                    observations = self.getObservations(world_state)
                    
                    #get observation
                    attempt = 0
                    while len(observations) <= 1:
                        observations = self.getObservations(world_state)
                        attempt += 1
                        if attempt == 10:
                            deadflag = 1
                            break
                    if deadflag == 1:
                        done_update = True
                        break
                    #get observation
                    
                    current_r = self.rewardCalculate(agent_host,observations,A[-1])
                    R.append(current_r)
                    if not observations['IsAlive'] or S[-1][0] == -100000:
                        # Terminating state
                        T = t + 1
                        S.append('Term State')
                        present_reward = current_r
                    else:

                        s = self.getState(observations)
               
                        S.append(s)
                        possible_actions = self.getActions(s)
                        next_a = self.choose_actions(s, possible_actions, self.epsilon)
                        self.pastActions.append(next_a)
                        A.append(next_a)
            
                tau = t - self.n + 1
    
                if tau >= 0:
                    
                    self.update_q_table(tau, S, A, R, T)

                if tau == T - 1:
                    while len(S) > 1:
                        tau = tau + 1
                        self.update_q_table(tau, S, A, R, T)

                    done_update = True
                    break
