# toponode.txt 拓扑点坐标文件
class TopoNode:

    def __init__(self, _id: int, xp: float, yp: float):
        self.id = _id
        self.xp = xp
        self.yp = yp


# conn.txt cont.txt 节点信息
class Node:

    def __init__(self, _id: int, _type: int, topo: TopoNode, neighIDList: list):
        self.id = _id
        self.type = _type
        self.topo = topo
        self.neighIDList = neighIDList


# topodlink.txt 描述拓扑路段结构的文件
class TopoLink:

    def __init__(self, _id: int, topoLinkList: list):
        self.id = _id
        self.topoLinkList = topoLinkList


# geom.txt node-toponode.txt link-topodlink.txt 路段信息
class Section:

    def __init__(self, _id: int, _type: int, grade: int, oPoint: Node, dPoint: Node, length: float, speed: int,
                 num: int, topoLink: TopoLink):
        self.id = _id
        self.type = _type
        self.grade = grade
        self.origin = oPoint
        self.dest = dPoint
        self.length = length
        self.speed = speed
        self.num = num
        self.topoDLink = topoLink
