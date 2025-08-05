from collections import deque

def hamiltonian_cycle(graph):
    vertices = [v[0] for v in graph.vertices]
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    path = [vertices[0]]

    def backtrack(pos):
        if len(path) == len(vertices):
            return path[0] in adjacency[path[-1]]
        for v in vertices:
            if v not in path and v in adjacency[path[-1]]:
                path.append(v)
                if backtrack(pos + 1):
                    return True
                path.pop()
        return False

    if backtrack(1):
        return path + [path[0]]
    return None

def hamiltonian_cycle_with_steps(graph, start_vertex=None):
    """Tìm chu trình Hamilton với chi tiết các bước, bắt đầu từ đỉnh được chỉ định"""
    vertices = [v[0] for v in graph.vertices]
    if len(vertices) == 0:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': 'Đồ thị rỗng - không có đỉnh nào'}],
            'total_steps': 1
        }
    
    if len(vertices) == 1:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [vertices[0]], 'action': 'Đồ thị chỉ có 1 đỉnh - không thể tạo chu trình'}],
            'total_steps': 1
        }
    
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    # Kiểm tra điều kiện cần thiết
    isolated_vertices = [v for v in vertices if len(adjacency[v]) == 0]
    if isolated_vertices:
        return {
            'success': False,
            'path': None,
            'steps': [
                {'step': 1, 'path': [], 'action': f'Có đỉnh cô lập: {", ".join(isolated_vertices)}'},
                {'step': 2, 'path': [], 'action': 'Không thể tạo chu trình Hamilton với đỉnh cô lập'}
            ],
            'total_steps': 2
        }

    # Nếu không có đỉnh bắt đầu được chỉ định, chọn đỉnh đầu tiên
    start_vertex = start_vertex if start_vertex in vertices else vertices[0]
    path = [start_vertex]
    steps = []
    step_count = 0

    # Bước khởi tạo
    step_count += 1
    steps.append({
        'step': step_count,
        'path': path.copy(),
        'action': f"Khởi tạo: Bắt đầu từ đỉnh {start_vertex}"
    })

    def backtrack(pos):
        nonlocal step_count
        
        if len(path) == len(vertices):
            step_count += 1
            steps.append({
                'step': step_count,
                'path': path.copy(),
                'action': f"Đã thăm tất cả {len(vertices)} đỉnh: {' → '.join(path)}"
            })
            
            if path[0] in adjacency[path[-1]]:
                step_count += 1
                final_path = path + [path[0]]
                steps.append({
                    'step': step_count,
                    'path': final_path,
                    'action': f"Thành công! Có cạnh từ {path[-1]} về {path[0]} - Chu trình: {' → '.join(final_path)}"
                })
                return True
            else:
                step_count += 1
                steps.append({
                    'step': step_count,
                    'path': path.copy(),
                    'action': f"Không có cạnh từ {path[-1]} về {path[0]} - Không tạo được chu trình"
                })
                return False
        
        # Thử các đỉnh kề
        current_vertex = path[-1]
        neighbors = [v for v in vertices if v not in path and v in adjacency[current_vertex]]
        
        if not neighbors:
            step_count += 1
            steps.append({
                'step': step_count,
                'path': path.copy(),
                'action': f"Không có đỉnh kề khả dụng từ {current_vertex}"
            })
            return False
        
        step_count += 1
        steps.append({
            'step': step_count,
            'path': path.copy(),
            'action': f"Từ {current_vertex}, thử các đỉnh: {', '.join(neighbors)}"
        })
        
        for v in neighbors:
            step_count += 1
            path.append(v)
            steps.append({
                'step': step_count,
                'path': path.copy(),
                'action': f"Thêm đỉnh {v} vào đường đi: {' → '.join(path)}"
            })
            
            if backtrack(pos + 1):
                return True
            
            # Backtrack
            path.pop()
            step_count += 1
            steps.append({
                'step': step_count,
                'path': path.copy(),
                'action': f"Quay lui: Loại bỏ {v}, quay về {' → '.join(path) if path else 'rỗng'}"
            })
        
        return False

    success = backtrack(1)
    
    if not success and step_count > 1:
        step_count += 1
        steps.append({
            'step': step_count,
            'path': [],
            'action': f"Kết luận: Đã thử tất cả khả năng từ đỉnh {start_vertex} - Không tồn tại chu trình Hamilton"
        })
    
    result_path = path + [path[0]] if success else None
    
    return {
        'success': success,
        'path': result_path,
        'steps': steps,
        'total_steps': step_count
    }

def connected_components(graph):
    vertices = [v[0] for v in graph.vertices]
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    visited = set()
    count = 0

    def dfs(u):
        visited.add(u)
        for v in adjacency[u]:
            if v not in visited:
                dfs(v)

    for v in vertices:
        if v not in visited:
            dfs(v)
            count += 1

    return count