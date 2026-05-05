from collections import defaultdict, deque

class Graph:
    def __init__(self):
        # Default dictionary to store graph
        self.graph = defaultdict(list)

    def add_edge(self, u, v):
        self.graph[u].append(v)
        self.graph[v].append(u)  # Since it's undirected, add reverse edge

    def dfs_recursive(self, vertex, visited=None):
        if visited is None:
            visited = set()

        visited.add(vertex)
        print(vertex, end=' ')

        for neighbor in self.graph[vertex]:
            if neighbor not in visited:
                self.dfs_recursive(neighbor, visited)

    def bfs(self, start):
        visited = set()  # Track visited nodes
        queue = deque([start])  # Efficient queue implementation

        visited.add(start)

        while queue:
            vertex = queue.popleft()  # Remove front element
            print(vertex, end=' ')

            # Add all unvisited neighbors
            for neighbor in self.graph[vertex]:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)


# Example usage
g = Graph()

g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 3)
g.add_edge(1, 4)
g.add_edge(2, 5)
g.add_edge(2, 6)
g.add_edge(3, 7)
g.add_edge(4, 8)
g.add_edge(5, 9)
g.add_edge(6, 10)

print("Depth First Search (starting from vertex 0):")
g.dfs_recursive(0)

print("\nBreadth First Search (starting from vertex 0):")
g.bfs(0)