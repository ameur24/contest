"""Task: Create a wxPython class

wx.TreeCtrl is a widget that shows a tree that the user can expand and
collapse. Extend the wx.TreeCtrl class to automatically populate the
tree and react to changes to a data model.

Build upon the given framework code. When your solution is in use,
subclasses of TreeNode will provide the structure to be visualized.

Only query for the children of a node when necessary. Use established
coding practices and follow the code conventions in the existing
code. Be mindful that you create a library class. In particular, good
documentation is important. You're also encouraged to make notes of
potential problems and future improvements.
"""

import threading
from typing import *
from abc import ABC, abstractmethod

Observer = Callable[[], Any]

# All callbacks scheduled to be called
_callback_queue = set()
def process_callbacks() -> None:
    "Called on the WX thread"
    while _callback_queue:
        callback = _callback_queue.pop()
        callback()

class Observable:
    """When an Observable is *triggered* it notifies all its observers."""
    def __init__(self):
        self._observers : Set[Observer] = set()
    def add_observer(self, observer : Observer) -> None:
        self._observers.add(observer)
    def remove_observer(self, observer : Observer) -> None:
        self._observers.discard(observer)
    def notify_observers(self) -> None:
        "Makes all observers execute on the wxPython thread, asynchronously"
        invoke = (not _callback_queue)
        _callback_queue.update(self._observers)
        if invoke:
            wx.CallLater(process_callbacks)

ValueType = TypeVar('ValueType')

class ObsVar(Observable, Generic[ValueType]):
    """An ObsVar (OBServable VARiable) notifies its observers when the
    value of get() changes.
    """
    def __init__(self, value : ValueType):
        self._value = value
    def get(self) -> ValueType:
        return self._value
    def set(self, value : ValueType) -> None:
        if value != self._value:
            self._value = value
            self.notify_observers()

class TreeNode(ABC):
    "A node in a tree data structure in the data model"
    tree_label : ObsVar[str]
    @abstractmethod
    def is_tree_leaf(self) -> bool:
        """If True, get_tree_children() will never return any
        nodes. The value is constant for each TreeNode."""
        ...
    @abstractmethod
    def get_tree_children(self) -> 'Iterable[TreeNode]':
        ...
    # Notifies when the return value of get_tree_children() may have changed
    tree_children_change : Observable




import wx
class TreeCtrl(wx.TreeCtrl):
    "Extends wx.TreeCtrl to use TreeNode as data model"
    def __init__(self, root: TreeNode, parent: wx.Window):
        super().__init__(parent)
        self._lock = threading.Lock()
        self._nodes_map = {}  # maps nodes to tree items
        self._tree_item_map = {}  # maps tree items to nodes
        self._root = root
        self._root_item = self.AddRoot(root.tree_label.get())
        self._nodes_map[root] = self._root_item
        self._tree_item_map[self._root_item] = root
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_item_expand)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_item_collapse)
        root.tree_label.add_observer(self.on_label_change)
        root.tree_children_change.add_observer(self.on_children_change)

    def on_item_expand(self, event):
        item = event.GetItem()
        node = self._tree_item_map[item]
        self._populate_children(item, node)

    def on_item_collapse(self, event):
        item = event.GetItem()
        self.DeleteChildren(item)

    def on_children_change(self):
        with self._lock:
            for node, item in self._nodes_map.items():
                if item and self.IsExpanded(item):
                    self.DeleteChildren(item)
                    self._populate_children(item, node)


    def on_label_change(self):
        with self._lock:
            for node, item in self._nodes_map.items():
                if item:
                    self.SetItemText(item, node.tree_label.get())



    def _populate_children(self, item: wx.TreeItemId, node: TreeNode):
        for child_node in node.get_tree_children():
            child_item = self.AppendItem(item, child_node.tree_label.get())
            self._nodes_map[child_node] = child_item
            self._tree_item_map[child_item] = child_node
            child_node.tree_label.add_observer(self.on_label_change)
            child_node.tree_children_change.add_observer(self.on_children_change)
