#parse AST text file
#output shape depending on node type
#connect nodes according to tree edges
#offset, extrude, cap all tree edges

import rhinoscriptsyntax as rs
import math
import random

ast_file = open(ast_file)

node_list = ast_file.readlines()

tree = {}
first_node = node_list[0]
first_indent = len(first_node)-len(first_node.lstrip())
first_cleaned = first_node.strip()
tree[first_cleaned] = []

parent_map = {}
parent_map[0] = (tree[first_cleaned],-1)

def build_tree(curr_subtree, curr_sub_index, prev_indent, index, max_index):
	if index > max_index:
		return

	curr_node = node_list[index]
	curr_indent = len(curr_node) - len(curr_node.lstrip())
	cleaned_node = curr_node.strip()
	subtree = {}
	subtree[cleaned_node] = []

	if curr_indent > prev_indent:
		#it is a child of the prev node
		curr_subtree.append(subtree)
		parent_map[index] = (curr_subtree,curr_sub_index)
	else:
		# traverse up the tree to find the prev node w the same indentation
		# that node is the sibling of the curr node
		# add curr node as a child of that node's parent
		parent_indent = prev_indent
		new_index = curr_sub_index
		new_parent = curr_subtree
		while curr_indent < parent_indent:
			new_parent, new_index = parent_map[new_index]
			parent_val = node_list[new_index]
			parent_indent = len(parent_val)-len(parent_val.lstrip())
		#now new_parent is a sibling of subtree
		final_parent, final_index = parent_map[new_index]
		parent_map[index] = (final_parent,final_index)
		final_parent.append(subtree)

	build_tree(subtree[cleaned_node],index,curr_indent,index+1,max_index)
			
def print_dict(space,dict):
	for k,v in dict.items():
		print(space,k)
		for i in v:
			print_dict(space+"\t",i)	

#call the builder		
build_tree(tree[first_cleaned],0,first_indent,1,len(node_list)-1)

#now traverse the tree and transform into geometry
type_shape_map = {}
unvisited = []

final_node_list = []
final_edge_list = []
center_points = []

#create shape for root
root_type = list(tree.keys())[0]
type_shape_map[root_type] = shapes[random.randint(0,len(shapes)-1)]

#this means the root will be placed right on top of input sample shape
#can just move after baking so no longer overlaps
root_shape = type_shape_map[root_type].Duplicate() 
final_node_list.append(root_shape)
unvisited.append((root_shape,tree))

while unvisited:
	curr_node, curr_dict = unvisited.pop(0)
	root, child_list = list(curr_dict.items())[0]
	
	child_shape_list = []
	
	#BFS traversal to gen shapes for all nodes
	for child in child_list:
		child_type = list(child.keys())[0]
		if child_type not in type_shape_map:
			type_shape = shapes[random.randint(0,len(shapes)-1)]
			type_shape_map[child_type] = type_shape
		child_shape = type_shape_map[child_type].Duplicate()
		child_shape_list.append(child_shape)
		unvisited.append((child_shape,child))
	
	#now actually construct the geometry from the child shapes
	#this step is why it needs to be BFS- so can distribute children properly
	
	test,pl = curr_node.TryGetPolyline()
	if test:
		#this should always work as long as the input curves are polylines
		parent_center = pl.CenterPoint()
		center_points.append(parent_center)
		
		#if there is an odd num children, place center child directly below parent
		#then remove from list (doesn't need a custom angle_
		
		if len(child_shape_list) > 0:
			if len(child_shape_list)%2:
				new_center = rs.CreatePoint(parent_center.X,parent_center.Y-drop_dist)
				center_points.append(new_center)
				middle_child = child_shape_list.pop(int(len(child_shape_list)/2))
				#move from current center to new center
				test,pl = middle_child.TryGetPolyline()
				middle_center = pl.CenterPoint()
				rs.MoveObject(middle_child, new_center-middle_center)
				edge = rs.AddLine(parent_center, new_center)
				final_node_list.append(middle_child)
				final_edge_list.append(edge)
			
			if len(child_shape_list) > 0:
				angle_step = max_fanout/len(child_shape_list)
				center_index = int(len(child_shape_list)/2)
		
				for i in range(0,len(child_shape_list)):
					curr_child = child_shape_list[i]
					test,pl = curr_child.TryGetPolyline()
					curr_center = pl.CenterPoint()
					if i<center_index:
						center_angle = angle_step*(center_index-i)
						x_off = drop_dist * math.tan(math.radians(center_angle))
						new_center = rs.CreatePoint(parent_center.X-x_off, parent_center.Y-drop_dist)
						rs.MoveObject(curr_child,new_center-curr_center)
						edge = rs.AddLine(parent_center, new_center)
						center_points.append(new_center)                      
						final_edge_list.append(edge)
						final_node_list.append(curr_child)
					else:
						center_angle = angle_step*(i-center_index+1)
						x_off = drop_dist * math.tan(math.radians(center_angle))
						new_center = rs.CreatePoint(parent_center.X+x_off,parent_center.Y-drop_dist)
						rs.MoveObject(curr_child,new_center-curr_center)
						edge = rs.AddLine(parent_center, new_center)
						center_points.append(new_center)                      
						final_edge_list.append(edge)
						final_node_list.append(curr_child)
					#movement and edge lines used to be here, 
					#but scoping was weird and only got half the nodes idk

out_nodes = final_node_list
out_edges = final_edge_list
out_points = center_points
