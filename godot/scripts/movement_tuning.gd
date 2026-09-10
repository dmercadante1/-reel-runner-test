class_name MovementTuning
extends Resource
## Provisional playfeel values; not final art or level specifications.

@export_range(60.0, 300.0, 1.0) var run_speed: float = 145.0
@export_range(100.0, 4000.0, 10.0) var acceleration: float = 1600.0
@export_range(100.0, 4000.0, 10.0) var braking: float = 2000.0
@export_range(300.0, 2200.0, 10.0) var gravity: float = 1000.0
@export_range(-600.0, -100.0, 1.0) var jump_speed: float = -330.0
@export_range(200.0, 1000.0, 10.0) var terminal_fall_speed: float = 650.0
@export_range(0.0, 0.2, 0.01) var coyote_seconds: float = 0.09
@export_range(0.0, 0.25, 0.01) var jump_buffer_seconds: float = 0.12
@export_range(0.1, 0.9, 0.05) var release_jump_multiplier: float = 0.45
