import torch.nn as nn

class digitRecognizer(nn.Module):
  
  def __init__(self, input_size, hidden_layers, num_classes):
    super(digitRecognizer, self).__init__()
    self.input = nn.Linear(in_features=input_size, out_features=hidden_layers)
    
    self.relu_1 = nn.ReLU()
    self.hidden_1 = nn.Linear(in_features=hidden_layers, out_features=hidden_layers)
    self.relu_2 = nn.ReLU()
    self.hidden_2 = nn.Linear(in_features=hidden_layers, out_features=hidden_layers)
    self.relu_3 = nn.ReLU()
    self.hidden_3 = nn.Linear(in_features=hidden_layers, out_features=hidden_layers)
    self.relu_4 = nn.ReLU()
    
    self.output = nn.Linear(in_features=hidden_layers, out_features=num_classes)

  def forward(self, x):
    model = self.input(x)
    
    model = self.relu_1(model)
    model = self.hidden_1(model)
    model = self.relu_2(model)
    model = self.hidden_2(model)
    model = self.relu_3(model)
    model = self.hidden_3(model)
    model = self.relu_4(model)
    
    model = self.output(model)

    return model