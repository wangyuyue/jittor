
# ***************************************************************
# Copyright (c) 2020 Jittor. Authors: 
#     Wenyang Zhou <576825820@qq.com>
#     Dun Liang <randonlang@gmail.com>. 
# All Rights Reserved.
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
# ***************************************************************
# This model is generated by pytorch converter.
import jittor as jt
from jittor import nn

__all__ = ['ShuffleNetV2', 'shufflenet_v2_x0_5', 'shufflenet_v2_x1_0', 'shufflenet_v2_x1_5', 'shufflenet_v2_x2_0']

def channel_shuffle(x, groups):
    (batchsize, num_channels, height, width) = x.data.shape
    channels_per_group = (num_channels // groups)
    x = jt.reshape(x, [batchsize, groups, channels_per_group, height, width])
    x = jt.transpose(x, (0,2,1,3,4))
    x = jt.reshape(x, [batchsize, (- 1), height, width])
    return x

class InvertedResidual(nn.Module):

    def __init__(self, inp, oup, stride):
        super(InvertedResidual, self).__init__()
        if (not (1 <= stride <= 3)):
            raise ValueError('illegal stride value')
        self.stride = stride
        branch_features = (oup // 2)
        assert ((self.stride != 1) or (inp == (branch_features << 1)))
        if (self.stride > 1):
            self.branch1 = nn.Sequential(self.depthwise_conv(inp, inp, kernel_size=3, stride=self.stride, padding=1), nn.BatchNorm(inp), nn.Conv(inp, branch_features, kernel_size=1, stride=1, padding=0, bias=False), nn.BatchNorm(branch_features), nn.Relu())
        else:
            self.branch1 = nn.Sequential()
        self.branch2 = nn.Sequential(nn.Conv((inp if (self.stride > 1) else branch_features), branch_features, kernel_size=1, stride=1, padding=0, bias=False), nn.BatchNorm(branch_features), nn.Relu(), self.depthwise_conv(branch_features, branch_features, kernel_size=3, stride=self.stride, padding=1), nn.BatchNorm(branch_features), nn.Conv(branch_features, branch_features, kernel_size=1, stride=1, padding=0, bias=False), nn.BatchNorm(branch_features), nn.Relu())

    @staticmethod
    def depthwise_conv(i, o, kernel_size, stride=1, padding=0, bias=False):
        return nn.Conv(i, o, kernel_size, stride, padding, bias=bias, groups=i)

    def execute(self, x):
        if (self.stride == 1):
            x1 = x[:,0:x.shape[1]//2]
            x2 = x[:,x.shape[1]//2:x.shape[1]]
            out = jt.contrib.concat([x1, self.branch2(x2)], dim=1)
        else:
            out = jt.contrib.concat([self.branch1(x), self.branch2(x)], dim=1)
        out = channel_shuffle(out, 2)
        return out

class ShuffleNetV2(nn.Module):

    def __init__(self, stages_repeats, stages_out_channels, num_classes=1000, inverted_residual=InvertedResidual):
        super(ShuffleNetV2, self).__init__()
        if (len(stages_repeats) != 3):
            raise ValueError('expected stages_repeats as list of 3 positive ints')
        if (len(stages_out_channels) != 5):
            raise ValueError('expected stages_out_channels as list of 5 positive ints')
        self._stage_out_channels = stages_out_channels
        input_channels = 3
        output_channels = self._stage_out_channels[0]
        self.conv1 = nn.Sequential(nn.Conv(input_channels, output_channels, 3, 2, 1, bias=False), nn.BatchNorm(output_channels), nn.Relu())
        input_channels = output_channels
        self.maxpool = nn.Pool(kernel_size=3, stride=2, padding=1, op='maximum')
        stage_names = ['stage{}'.format(i) for i in [2, 3, 4]]
        for (name, repeats, output_channels) in zip(stage_names, stages_repeats, self._stage_out_channels[1:]):
            seq = [inverted_residual(input_channels, output_channels, 2)]
            for i in range((repeats - 1)):
                seq.append(inverted_residual(output_channels, output_channels, 1))
            setattr(self, name, nn.Sequential(*seq))
            input_channels = output_channels
        output_channels = self._stage_out_channels[(- 1)]
        self.conv5 = nn.Sequential(nn.Conv(input_channels, output_channels, 1, 1, 0, bias=False), nn.BatchNorm(output_channels), nn.Relu())
        self.fc = nn.Linear(output_channels, num_classes)

    def _forward_impl(self, x):
        x = self.conv1(x)
        x = self.maxpool(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.stage4(x)
        x = self.conv5(x)
        x = x.mean([2, 3])
        x = self.fc(x)
        return x

    def execute(self, x):
        return self._forward_impl(x)

def _shufflenetv2(arch, *args):
    model = ShuffleNetV2(*args)
    return model

def shufflenet_v2_x0_5(pretrained=False):
    model = _shufflenetv2('shufflenetv2_x0.5', [4, 8, 4], [24, 48, 96, 192, 1024])
    if pretrained: model.load("jittorhub://shufflenet_v2_x0_5.pkl")
    return model

def shufflenet_v2_x1_0(pretrained=False):
    model = _shufflenetv2('shufflenetv2_x1.0', [4, 8, 4], [24, 116, 232, 464, 1024])
    if pretrained: model.load("jittorhub://shufflenet_v2_x1_0.pkl")
    return model

def shufflenet_v2_x1_5(pretrained=False):
    model = _shufflenetv2('shufflenetv2_x1.5', [4, 8, 4], [24, 176, 352, 704, 1024])
    if pretrained: model.load("jittorhub://shufflenet_v2_x1_5.pkl")
    return model

def shufflenet_v2_x2_0(pretrained=False):
    model = _shufflenetv2('shufflenetv2_x2.0', [4, 8, 4], [24, 244, 488, 976, 2048])
    if pretrained: model.load("jittorhub://shufflenet_v2_x2_0.pkl")
    return model
