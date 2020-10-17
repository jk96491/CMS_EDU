import torch
from Week03.Example.Model import MyModel
import torch.optim as optim
import random
import numpy as np

use_cuda = True

input_size = 3
output_size = 1
hidden_size = 0
hidden_dim = 1

subject_score_list = []
final_score_list = []

for i in range(10000):
    kor = random.randrange(10, 100)
    math = random.randrange(10, 100)
    eng = random.randrange(10, 100)
    subject_score_list.append([kor, math, eng])

    final_score = (kor + math + eng) / 3.0

    final_score_list.append([final_score])

if use_cuda:
    x_train = torch.FloatTensor(subject_score_list).cuda()
    y_train = torch.FloatTensor(final_score_list).cuda()
    model = MyModel(hidden_size, input_size, output_size, hidden_dim).cuda()
else:
    x_train = torch.FloatTensor(subject_score_list)
    y_train = torch.FloatTensor(final_score_list)
    model = MyModel(hidden_size, input_size, output_size, hidden_dim)


optimizer = optim.Adam(model.parameters(), lr=0.001)

nb_epochs = 15000
for epoch in range(nb_epochs + 1):

    s = np.arange(x_train.shape[0])
    np.random.shuffle(s)

    rand = random.randrange(50, 100)

    x_train = x_train[s]
    y_train = y_train[s]

    x_train = x_train[:rand]
    y_train = y_train[:rand]

    prediction = model(x_train * 0.01)
    cost = torch.mean((prediction - y_train * 0.01)**2)

    optimizer.zero_grad()
    cost.backward()
    optimizer.step()

    print('Epoch {:4d}/{} Cost: {:.6f}'.format(epoch, nb_epochs, cost.item()))
    print(model.layers[0].weight.data[0])

torch.save(model.state_dict(), 'Train_model/model.th')