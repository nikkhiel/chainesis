
# coding: utf-8

# In[ ]:


import os
from web3 import Web3, HTTPProvider
from interface import ContractInterface
#ContractInterface is giving error on Windows10

# This imports a few methods from the web3.py library along with the ContractInterface class from interface.py. Next, we’ll want to create our web3 instance using:

# In[ ]:


w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))


# Those are ganache’s default host and port. You can now interact with your node through python. Feel free to run the above commands in a python interperter, like:

# In[ ]:


Those are ganache’s default host and port. You can now interact with your node through python. Feel free to run the above commands in a python interperter, like:


# In[ ]:


from web3 import Web3, HTTPProvider
w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))
w3.eth.accounts[0] #should return:
0xf52cef744ccdd52e66856057d820d2b6677af63c #account 0 from above


# In[ ]:


Nifty.

On the next line set up the path variable for where your contracts are stored, if you’re just using the included contracts that will look like:


# In[ ]:


contract_dir = os.path.abspath('./contracts/')


# In[ ]:


And finally, you’ll want to create an interface instance with:


# In[1]:


greeter_interface = ContractInterface(w3, 'Greeter', contract_dir)


# In[ ]:


‘Greeter’ here is the name of the contract you wish to create an interface for. Since Greeter.sol inherits from Owned.sol, you’ll have access to all the methods within Owned from the Greeter interface.

Let’s run walkthrough.py briefly with the following to make sure we aren’t getting any errors on initialization:


# In[ ]:


python3 -i walkthrough.py
type(greeter_interface)


# In[ ]:


Should return <class 'interface.ContractInterface'>

Also, if you need a quick reference for any of the interface methods, you can run >>> help(ContractInterface) for docstring output.

Compile

Solc is (rightly so) pretty strict about compiling dependencies that aren’t passed explicitly. Everything was compiling fine when using Truffle, but Solc took some tinkering. If you’re importing contracts, make sure you use this specific format import "./contract.sol"; below your pragma. The compiler should take care of the rest. Go ahead and add the following to walkthrough.py:

greeter_interface.compile_source_files()

At this point, walkthrough should look like


# In[ ]:


# Put your imports here
import os
from interface import ContractInterface
from web3 import HTTPProvider, Web3

# Initialize your web3 object
w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))

# Create a path object to your Solidity source files
contract_dir = os.path.abspath('./contracts/')

# Initialize your interface
greeter_interface = ContractInterface(w3, 'Greeter', contract_dir)

# Compile contracts below
greeter_interface.compile_source_files()


# In[ ]:


Let’s look at the compile_source_files() method in more detail:


# In[ ]:


deployment_list = []

for contract in os.listdir(self.contract_directory):
    deployment_list.append(
        os.path.join(self.contract_directory,  contract)
    )

self.all_compiled_contracts = compile_files(deployment_list)

print('Compiled contract keys:\n{}'.format(
        '\n'.join(self.all_compiled_contracts.keys())
    ))


# In[ ]:


This method just created a list of absolute paths to be passed to py-solc’s compile_files. The compiler output is then saved to an instance attribute for later use. If you now run walkthrough you should see the compiled contract keys print out.
Deploy

Let’s add the deployment method to walkthrough with the line:


# In[ ]:


greeter_interface.deploy_contract()


# In[ ]:


This method first checks that the contracts are compiled and re-compiles them if not with the following:


# In[ ]:


try:
    self.all_compiled_contracts is not None
except AttributeError:
    print("Source files not compiled, compiling now and trying again...")
    self.compile_source_files()


# In[ ]:


Next, it will find the name of the contract we specified to deploy earlier within one of the compiler output keys. It then creates a deployment instance using that contract’s application binary interface (ABI) and bytecode (BIN):


# In[ ]:


for compiled_contract_key in self.all_compiled_contracts.keys():
    if self.contract_to_deploy in compiled_contract_key:
        deployment_compiled = self.all_compiled_contracts[
            compiled_contract_key
        ]

deployment = self.web3.eth.contract(
    abi=deployment_compiled['abi'],
    bytecode=deployment_compiled['bin']
    )


# In[ ]:


This is our first time seeing the web3.py library in action. The web3.eth.contract is a contract class ready to be deployed on the blockchain. Next we’ll estimate the gas usage for deployment and deploy it if it’s below what was set during initialization.


# In[ ]:


deployment_estimate = deployment.constructor().estimateGas(
    transaction=deployment_params)

if deployment_estimate < self.max_deploy_gas:
    tx_hash = deployment.constructor().transact(
        transaction=deployment_params)


# In[ ]:


A few things are happening here. The constructor() method builds the deployment transaction given deployment_params. This is a dictionary with a number of defaults that can be overloaded if desired. The max_deploy_gas is set as a default during __init__ and is really just a safety feature for unexpected deployment gas usage. If that passes, the contract is deployed using constructor().transact and the transaction hash (tx_hash) is returned.


# In[ ]:


tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']


# In[ ]:


These two lines wait for the transaction to be mined, return the receipt, and pull the contract’s address from it. We’re going to write that to file with the following:


# In[ ]:


vars = {
    'contract_address' : contract_address,
    'contract_abi' : deployment_compiled['abi']
}

with open (self.deployment_vars_path, 'w') as write_file:
    json.dump(vars, write_file, indent=4)


# In[ ]:


This collects the deployment address and the contract’s ABI and saves them to a JSON file at the path specified in deployment_vars_path. We’ll see why in the next section.

Now if you run walkthrough you should see the output from compiling the contracts, some contract deployment output and a line telling you where those variables were saved.
Getting an Instance

Once we deploy a contract to the blockchain, it will persist there indefinitely (in theory at least). We don’t want to re-compile and re-deploy every time we want to interact with it. This is why we saved the contract’s address and ABI in the JSON file in the last section. Add the following to walkthrough:


# In[ ]:


greeter_interface.get_instance()


# In[ ]:


The first part of this method will open up the JSON, check that it has an address, and then check that there’s something deployed at that address with:


# In[ ]:


with open (self.deployment_vars_path, 'r') as read_file:
    vars = json.load(read_file)

try:
    self.contract_address = vars['contract_address']
except ValueError(
    "No address found in {}, please call 'deploy_contract' and 
    try again.".format(self.deployment_vars_path)
    ):
    raise

contract_bytecode_length = len(self.web3.eth.getCode(
     self.contract_address).hex())

try:
    assert (contract_bytecode_length > 4), "Contract not deployed 
    at {}.".format(self.contract_address)
except AssertionError as e:
    print(e)
    raise
else:
    print('Contract deployed at {}. This function returns 
          an instance object.'.format(self.contract_address))


# In[ ]:


Once those checks are done, we’ll build the contract instance again, using the address this time and return that instance.


# In[ ]:


self.contract_instance = self.web3.eth.contract(
     abi = vars['contract_abi'],
     address = vars['contract_address']
     )

return self.contract_instance


# In[ ]:


This deployed instance exposes your contract’s properties and methods as outlined in the documentation. For example,


# In[ ]:


>>>instance = greeter_interface.get_instance()
>>>instance.functions.greet().call()
>>>b'Hello'\x00\x00\x00\x00...


# In[ ]:


The greeting shows up like this because it’s set as the type bytes32 in Greeter.sol. We’ll explore why I went with bytes, along with dealing with events, and cleaning outputs in part 2 of this tutorial! However, for a lot of people, this contract instance will be enough to suit their needs.

Wrap Up

I wrote this little interface because I wanted a clean way to compile, deploy, and interact with smart contracts from Python. It’s been a big learning experience for me and the result of a lot of tinkering — I hope it’s helpful to some of you out there. However, it is fairly opinionated and certainly not as robust as I’d like it to be. It’s very much a work in progress and I’m open to criticisms and improvements. Also, again, if you need any help along the way, leave a comment and I’ll do my best!
Ethereum
Python
Python Ethereum
Python Ethereum Interface
Ethereum Interface

