from collections import deque
import itertools

def check_hamiltonian_conditions(graph):
    """Kiểm tra điều kiện cần cho chu trình Hamilton dựa trên định lý Dirac"""
    vertices = [v[0] for v in graph.vertices]
    n = len(vertices)
    if n < 3:
        return False, "Đồ thị cần ít nhất 3 đỉnh để có chu trình Hamilton"
    
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    
    for v in vertices:
        if len(adjacency[v]) < n / 2:
            return False, f"Đỉnh {v} có bậc {len(adjacency[v])} < {n/2}, không thỏa định lý Dirac"
    return True, "Đồ thị thỏa điều kiện cần của định lý Dirac"

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

    # Kiểm tra đồ thị liên thông
    if connected_components(graph) > 1:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': 'Đồ thị không liên thông - không thể có chu trình Hamilton'}],
            'total_steps': 1
        }
    
    # Kiểm tra điều kiện cần (Dirac)
    is_valid, message = check_hamiltonian_conditions(graph)
    if not is_valid:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': message}],
            'total_steps': 1
        }
    
    # Kiểm tra điều kiện cần thiết (đỉnh cô lập)
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
                    'action': f"Thành công! Có cạnh từ {path[-1]} về {path[0]}\nChu trình Hamilton là: {' → '.join(final_path)}"
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

def hamiltonian_cycle_branch_and_bound(graph, start_vertex=None):
    """Tìm chu trình Hamilton bằng Branch and Bound với chi tiết các bước"""
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

    # Kiểm tra đồ thị liên thông
    if connected_components(graph) > 1:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': 'Đồ thị không liên thông - không thể có chu trình Hamilton'}],
            'total_steps': 1
        }
    
    # Kiểm tra điều kiện cần (Dirac)
    is_valid, message = check_hamiltonian_conditions(graph)
    if not is_valid:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': message}],
            'total_steps': 1
        }
    
    # Kiểm tra điều kiện cần thiết (đỉnh cô lập)
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
        'action': f"Khởi tạo (Nhánh cận): Bắt đầu từ đỉnh {start_vertex}"
    })

    def is_promising(path, current_vertex):
        """Kiểm tra xem việc thêm đỉnh current_vertex có tiềm năng dẫn đến lời giải"""
        # Nếu không có cạnh từ đỉnh hiện tại đến các đỉnh chưa thăm
        neighbors = [v for v in vertices if v not in path and v in adjacency[current_vertex]]
        if not neighbors and len(path) < len(vertices):
            return False, f"Không có đỉnh kề khả dụng từ {current_vertex}"
        
        # Nếu đã thăm đủ đỉnh, kiểm tra cạnh quay về đỉnh đầu
        if len(path) == len(vertices):
            if path[0] not in adjacency[current_vertex]:
                return False, f"Không có cạnh từ {current_vertex} về {path[0]}"
        
        # Kiểm tra tính liên thông của các đỉnh chưa thăm
        remaining_vertices = [v for v in vertices if v not in path]
        if remaining_vertices:
            temp_graph = {v: set(adjacency[v]) for v in remaining_vertices}
            for v in remaining_vertices:
                temp_graph[v] = {u for u in temp_graph[v] if u in remaining_vertices}
            if connected_components_temp(temp_graph, remaining_vertices) > 1:
                return False, f"Các đỉnh chưa thăm không liên thông"
        
        return True, ""

    def connected_components_temp(temp_graph, vertices):
        """Tính số miền liên thông trong tập đỉnh chưa thăm"""
        visited = set()
        count = 0

        def dfs(u):
            visited.add(u)
            for v in temp_graph[u]:
                if v not in visited:
                    dfs(v)

        for v in vertices:
            if v not in visited:
                dfs(v)
                count += 1
        return count

    def branch_and_bound(pos):
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
                    'action': f"Thành công! Có cạnh từ {path[-1]} về {path[0]}\nChu trình Hamilton là: {' → '.join(final_path)}"
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
            path.append(v)
            is_valid, reason = is_promising(path, v)
            if is_valid:
                step_count += 1
                steps.append({
                    'step': step_count,
                    'path': path.copy(),
                    'action': f"Thêm đỉnh {v} vào đường đi (hứa hẹn): {' → '.join(path)}"
                })
                
                if branch_and_bound(pos + 1):
                    return True
                
                # Backtrack
                path.pop()
                step_count += 1
                steps.append({
                    'step': step_count,
                    'path': path.copy(),
                    'action': f"Quay lui: Loại bỏ {v}, quay về {' → '.join(path) if path else 'rỗng'}"
                })
            else:
                path.pop()
                step_count += 1
                steps.append({
                    'step': step_count,
                    'path': path.copy(),
                    'action': f"Loại bỏ {v} vì: {reason}"
                })
        
        return False

    success = branch_and_bound(1)
    
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

def hamiltonian_cycle_brute_force(graph, start_vertex=None):
    """Tìm chu trình Hamilton bằng Brute Force (hoán vị) với chi tiết các bước"""
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

    # Kiểm tra đồ thị liên thông
    if connected_components(graph) > 1:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': 'Đồ thị không liên thông - không thể có chu trình Hamilton'}],
            'total_steps': 1
        }
    
    # Kiểm tra điều kiện cần (Dirac)
    is_valid, message = check_hamiltonian_conditions(graph)
    if not is_valid:
        return {
            'success': False,
            'path': None,
            'steps': [{'step': 1, 'path': [], 'action': message}],
            'total_steps': 1
        }
    
    # Kiểm tra điều kiện cần thiết (đỉnh cô lập)
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
    steps = []
    step_count = 0

    # Bước khởi tạo
    step_count += 1
    steps.append({
        'step': step_count,
        'path': [start_vertex],
        'action': f"Khởi tạo (Brute Force): Bắt đầu từ đỉnh {start_vertex}"
    })

    # Tạo tất cả hoán vị của các đỉnh còn lại
    remaining_vertices = [v for v in vertices if v != start_vertex]
    permutations = list(itertools.permutations(remaining_vertices))

    step_count += 1
    steps.append({
        'step': step_count,
        'path': [start_vertex],
        'action': f"Tạo tất cả hoán vị của các đỉnh còn lại: {', '.join(remaining_vertices)}"
    })

    # Kiểm tra từng hoán vị
    for perm in permutations:
        path = [start_vertex] + list(perm)
        step_count += 1
        steps.append({
            'step': step_count,
            'path': path.copy(),
            'action': f"Kiểm tra hoán vị: {' → '.join(path)}"
        })

        is_valid = True
        # Kiểm tra các cạnh liên tiếp
        for i in range(len(path) - 1):
            if path[i+1] not in adjacency[path[i]]:
                is_valid = False
                step_count += 1
                steps.append({
                    'step': step_count,
                    'path': path.copy(),
                    'action': f"Hoán vị không hợp lệ: Không có cạnh từ {path[i]} đến {path[i+1]}"
                })
                break
        
        if is_valid:
            # Kiểm tra cạnh từ đỉnh cuối về đỉnh đầu
            if path[0] in adjacency[path[-1]]:
                step_count += 1
                final_path = path + [path[0]]
                steps.append({
                    'step': step_count,
                    'path': final_path,
                    'action': f"Thành công! Có cạnh từ {path[-1]} về {path[0]}\nChu trình Hamilton là: {' → '.join(final_path)}"
                })
                return {
                    'success': True,
                    'path': final_path,
                    'steps': steps,
                    'total_steps': step_count
                }
            else:
                step_count += 1
                steps.append({
                    'step': step_count,
                    'path': path.copy(),
                    'action': f"Hoán vị không hợp lệ: Không có cạnh từ {path[-1]} về {path[0]}"
                })

    # Nếu không tìm thấy chu trình Hamilton
    step_count += 1
    steps.append({
        'step': step_count,
        'path': [],
        'action': f"Kết luận: Đã thử tất cả hoán vị từ đỉnh {start_vertex} - Không tồn tại chu trình Hamilton"
    })

    return {
        'success': False,
        'path': None,
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