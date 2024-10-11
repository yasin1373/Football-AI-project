from video_utils import read_video, save_video
from tracker_file import Tracker
import cv2
import numpy as np
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
from heatmap import HeatmapAndZones  # Import the heatmap and zone class

# Read Video
video_frames = read_video('Football_video.mp4')

# Initialize Tracker
tracker = Tracker('best.pt')

tracks = tracker.get_object_tracks(video_frames,
                                    read_from_stub=True,
                                    stub_path='track_stubs.pkl')

# Get object positions
tracker.add_position_to_tracks(tracks)

# Camera movement estimator
camera_movement_estimator = CameraMovementEstimator(video_frames[0])
camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                            read_from_stub=True,
                                                                            stub_path='camera_movement_stub.pkl')
camera_movement_estimator.add_adjust_positions_to_tracks(tracks, camera_movement_per_frame)

# View Transformer
view_transformer = ViewTransformer()
view_transformer.add_transformed_position_to_tracks(tracks)

# Interpolate Ball Positions
tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

# Speed and distance estimator
speed_and_distance_estimator = SpeedAndDistance_Estimator()
speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

# Initialize Heatmap and Zone Analysis
heatmap_and_zones = HeatmapAndZones()

# Generate Player Heatmaps (Optional: Can be done for individual players)
player_id = 3  # For example, generate heatmap for player with ID 3
heatmap_and_zones.generate_player_heatmap(tracks, player_id=player_id, save_path="player_3_heatmap.png")

# Analyze and Visualize Performance Zones
zones = [(0, 23), (23, 45), (45, 68)]  # Define zones: defense, midfield, attacking
zone_percentages = heatmap_and_zones.get_performance_zones(tracks, zones=zones, player_id=player_id)
heatmap_and_zones.visualize_performance_zones(zone_percentages, zones, save_path="player_3_zones.png")


# Draw output
## Draw object tracks
output_video_frames = tracker.draw_annotations(video_frames, tracks)

## Draw Camera movement
# output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames, camera_movement_per_frame)

## Draw Speed and Distance
speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

# Save analyzed video
save_video(output_video_frames, '/kaggle/working/output_video.mp4')
