import itertools
import random
import simpy

class Terminal:
    def __init__(self, env, num_berths, num_cranes, num_trucks):
        self.env = env
        self.berth = simpy.Resource(env, num_berths)
        self.cranes = simpy.Resource(env, num_cranes)
        self.trucks = [simpy.Resource(env, 1) for _ in range(num_trucks)]  # Individual resource for each truck

class Vessel:
    def __init__(self, name, terminal):
        self.name = name
        self.terminal = terminal
        self.env = terminal.env
        self.berth_id = None

    def process(self):
        print(f'{self.env.now:.2f} min: {self.name} arrives at the terminal.')
        yield self.env.process(self.request_berth())
        
        # Simulate the unloading process using all trucks
        for i in range(NUM_CONTAINERS):
            truck_id = i % NUM_TRUCKS  # Cycle through trucks for each container
            yield self.env.process(self.load_container(i, truck_id))

        self.terminal.berth.release(self.berth_request)  # Release the berth when done
        print(f'{self.env.now:.2f} min: {self.name} has finished unloading and leaves Berth {self.berth_id}.')

    def request_berth(self):
        self.berth_request = self.terminal.berth.request()
        yield self.berth_request
        self.berth_id = (self.berth_request.resource.count + 1) % NUM_BERTHS
        print(f'{self.env.now:.2f} min: {self.name} berths at Berth {self.berth_id}.')

    def load_container(self, container_id, truck_id):
        with self.terminal.trucks[truck_id].request() as req:  # Use specific truck
            yield req
            yield self.env.timeout(CRANE_TIME)
            print(f'{self.env.now:.2f} min: Crane at Berth {self.berth_id} unloads container {container_id + 1} onto Truck {truck_id + 1}.')
            
            yield self.env.timeout(TRUCK_TIME)
            print(f'{self.env.now:.2f} min: Truck {truck_id + 1} delivers container {container_id + 1} to yard block.')

def generate_vessels(env, terminal):
    count = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / INTER_ARRIVAL_TIME))
        vessel = Vessel(f'Vessel {count}', terminal)
        env.process(vessel.process())
        count += 1

# Constants
RANDOM_SEED = 42
INTER_ARRIVAL_TIME = 5 * 60  # Average time between vessel arrivals (in minutes)
NUM_CONTAINERS = 150
CRANE_TIME = 3  # Time to move one container (in minutes)
TRUCK_TIME = 6  # Time for truck to drop off container and return (in minutes)
NUM_BERTHS = 2
NUM_CRANES = 2
NUM_TRUCKS = 3

# Initialize simulation
print('Container Terminal Simulation')
random.seed(RANDOM_SEED)

# Taking user input for simulation time
SIMULATION_TIME = int(input("Enter the simulation time in minutes: "))

env = simpy.Environment()
terminal = Terminal(env, NUM_BERTHS, NUM_CRANES, NUM_TRUCKS)
env.process(generate_vessels(env, terminal))
env.run(until=SIMULATION_TIME)
print('Simulation finished.')
