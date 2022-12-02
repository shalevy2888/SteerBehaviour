GLOBAL_SCENE_MULTIPLY: float = 1.0
FAST_CHECK_INTERSECTION: bool = False

# Steering Behaviour Globals:
ahead_search_time: float = 0.5
separation_added_force_magnitude: float = 80
separation_with_front_only: bool = True
wander_divider: float = 4

flee_multiplier: float = -1

follow_velocity_multiplier: float = 1.8
seek_near_velocity_multiplier: float = 0.55
exact_follow_distance: float = 15
keep_pos_history = False
speed_mul_target_steps = 0.01

# Steering Behaviour Globals - these are sensitive to how big the entities are and should be multiplier by similar factor when changed
ahead_check_radius: float = 15 * GLOBAL_SCENE_MULTIPLY
path_target_radius: float = 12 * GLOBAL_SCENE_MULTIPLY
follow_slow_radius: float = 20 * GLOBAL_SCENE_MULTIPLY
wander_radius: float = 20 * GLOBAL_SCENE_MULTIPLY
separation_radius: float = 15 * GLOBAL_SCENE_MULTIPLY
line_size: float = 35 * GLOBAL_SCENE_MULTIPLY
path_leader_seek_radius: float = 80 * GLOBAL_SCENE_MULTIPLY

# Movable MovableEntityImpl Behaviour Globals - these are sensitive to how big the entities are and should be multiplier by similar factor when changed
target_reached_radius: float = 5 * GLOBAL_SCENE_MULTIPLY


def change_global_scene_multiplier(multiplier: float):
    global GLOBAL_SCENE_MULTIPLY, ahead_check_radius, path_target_radius, follow_slow_radius, wander_radius
    global separation_radius, target_reached_radius, line_size
    GLOBAL_SCENE_MULTIPLY = multiplier
    ahead_check_radius = 15 * GLOBAL_SCENE_MULTIPLY
    path_target_radius = 5 * GLOBAL_SCENE_MULTIPLY
    follow_slow_radius = 20 * GLOBAL_SCENE_MULTIPLY
    wander_radius = 20 * GLOBAL_SCENE_MULTIPLY
    separation_radius = 15 * GLOBAL_SCENE_MULTIPLY
    target_reached_radius = 5 * GLOBAL_SCENE_MULTIPLY
    line_size = 35 * GLOBAL_SCENE_MULTIPLY
