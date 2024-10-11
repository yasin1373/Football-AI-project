import numpy as np
import cv2
import matplotlib.pyplot as plt
import seaborn as sns

class HeatmapAndZones:
    def __init__(self, court_width=68, court_length=23.32, grid_size=(10, 10)):
        """
        Initialize the heatmap generator.
        court_width: The width of the court.
        court_length: The length of the court.
        grid_size: The resolution of the heatmap (number of rows and columns).
        """
        self.court_width = court_width
        self.court_length = court_length
        self.grid_size = grid_size

    def generate_player_heatmap(self, tracks, player_id=None, save_path=None):
        """
        Generate a heatmap for the given player or all players.
        player_id: Track a specific player by ID. If None, generate for all players.
        save_path: Path to save the generated heatmap.
        """
        heatmap_data = np.zeros(self.grid_size)  # Create a grid for the heatmap
        
        # Loop through each frame and collect the player positions
        for frame_num, player_tracks in enumerate(tracks['players']):
            for track_id, track_info in player_tracks.items():
                if player_id is not None and track_id != player_id:
                    continue  # Skip if not the specified player
                
                position = track_info.get('position_transformed')
                if position is None:
                    continue
                
                # Convert player position to grid coordinates
                grid_x = int((position[0] / self.court_length) * self.grid_size[1])
                grid_y = int((position[1] / self.court_width) * self.grid_size[0])
                
                # Increment the heatmap grid cell corresponding to the player's position
                heatmap_data[grid_y, grid_x] += 1
        
        # Plot the heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, cmap='coolwarm', linewidths=0.5, square=True)
        plt.title(f"Heatmap for Player {player_id if player_id else 'All Players'}")
        plt.xlabel('Field Length (Court X)')
        plt.ylabel('Field Width (Court Y)')
        
        if save_path:
            plt.savefig(save_path)
        plt.show()

    def get_performance_zones(self, tracks, zones, player_id=None):
        """
        Determine how much time the player or team spent in different performance zones.
        zones: List of zone boundaries, e.g., [(0, 10), (10, 30), (30, 68)] defines zones.
        player_id: Track a specific player by ID. If None, calculate for all players.
        """
        zone_times = np.zeros(len(zones))  # Keep track of time spent in each zone
        
        for frame_num, player_tracks in enumerate(tracks['players']):
            for track_id, track_info in player_tracks.items():
                if player_id is not None and track_id != player_id:
                    continue
                
                position = track_info.get('position_transformed')
                if position is None:
                    continue
                
                # Determine which zone the player is in based on their Y-position (court width)
                for zone_index, zone_boundary in enumerate(zones):
                    if zone_boundary[0] <= position[1] < zone_boundary[1]:
                        zone_times[zone_index] += 1  # Increment time spent in this zone
        
        # Normalize to get percentage of time spent in each zone
        total_time = np.sum(zone_times)
        zone_percentages = (zone_times / total_time) * 100 if total_time > 0 else np.zeros(len(zones))
        
        return zone_percentages

    def visualize_performance_zones(self, zone_percentages, zones, save_path=None):
        """
        Visualize the time spent in different performance zones using a bar plot.
        """
        zone_labels = [f"Zone {i+1} ({zones[i][0]}-{zones[i][1]}m)" for i in range(len(zones))]
        
        plt.figure(figsize=(10, 6))
        plt.bar(zone_labels, zone_percentages, color='skyblue')
        plt.ylabel('Time Spent (%)')
        plt.title('Player Performance in Different Zones')
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path)
        plt.show()