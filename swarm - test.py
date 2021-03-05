#2021-2-1
import arcade
import random, math, os
import numpy as np
from scipy.spatial import distance


file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)


WIDTH = 800
HEIGHT = 600
SPRITE_SCALING = 0.5
DEFAULT_BOIDS = 40


class MenuView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Menu Screen", self.window.width/2, self.window.height/2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.window.width/2, self.window.height/2-75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        instructions_view = InstructionView()
        self.window.show_view(instructions_view)


class InstructionView(arcade.View):
    def on_show(self):
        arcade.set_background_color((59, 98, 161))

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Instructions Screen", self.window.width/2, self.window.height/2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.window.width/2, self.window.height/2-75,
                         arcade.color.YELLOW, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.time_taken = 0

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.fish_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        #game settings
        self.debug = False

        for i in range(DEFAULT_BOIDS):
            self.SpawnBoid()

    def SpawnBoid(self):
        # Create the fish instance
        fish = arcade.Sprite(":resources:images/enemies/fishGreen.png", SPRITE_SCALING / 3, flipped_horizontally=True)
        # Position the fish
        fish.center_x = random.randrange(self.window.width)
        fish.center_y = random.randrange(self.window.height)
        fish.angle = random.uniform(-180,180)
        # Add the fish to the lists
        self.fish_list.append(fish)

    def on_show(self):
        arcade.set_background_color(arcade.color.BLUE_GREEN)

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

    def on_draw(self):
        arcade.start_render()
        # Draw all the sprites.
        self.player_list.draw()
        self.fish_list.draw()

        # arcade.draw_text("Me\n\n\n", self.player_sprite.center_x, self.player_sprite.center_y,
        #                  arcade.color.WHITE, 18, width=200, align="center", anchor_x="center",
        #                  anchor_y="center", rotation=0)

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 30, arcade.color.WHITE, 14)
        output_total = f"Total Score: {self.window.total_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

        #debugging display
        if self.debug:
            for fish in self.fish_list:
                if fish.neighbours:  # when there are neighbours
                    arcade.draw_line(start_x=fish.current_position[0], start_y=fish.current_position[1],
                                     end_x=fish.current_position[0]+fish.alignment_vector[0],
                                     end_y=fish.current_position[1]+fish.alignment_vector[1],
                                     color=arcade.color.GREEN, line_width=3)
                    arcade.draw_line(start_x=fish.current_position[0], start_y=fish.current_position[1],
                                     end_x=fish.current_position[0]+fish.cohesion_vector[0],
                                     end_y=fish.current_position[1]+fish.cohesion_vector[1],
                                     color=arcade.color.BLUE, line_width=3)
                    arcade.draw_line(start_x=fish.current_position[0], start_y=fish.current_position[1],
                                     end_x=fish.current_position[0] + fish.separation_vector[0],
                                     end_y=fish.current_position[1] + fish.separation_vector[1],
                                     color=arcade.color.RED, line_width=3)
                    arcade.draw_line(start_x=fish.current_position[0], start_y=fish.current_position[1],
                                     end_x=fish.current_position[0] + fish.target_velocity[0],
                                     end_y=fish.current_position[1] + fish.target_velocity[1],
                                     color=arcade.color.WHITE, line_width=1)

    def get_neightbours(self, current_fish, visual_range=60):
        neighbours = []
        for fish in self.fish_list:
            if current_fish != fish and distance.euclidean(current_fish.position, fish.position) <= visual_range:
                neighbours.append(fish)
        return neighbours

    def on_update(self, delta_time):
        self.time_taken += delta_time

        #loop through fishes
        for fish in self.fish_list:
            fish.target_velocity = np.array([0.0, 0.0])  # vector
            fish.current_velocity = np.array(fish.velocity)  # vector
            fish.current_position = np.array(fish.position)  # vector
            fish.nearest_position = np.array([np.inf, np.inf]) #for storing the location of the nearest neighbour
            fish.nearest_distance = np.inf
            fish.neighbours = self.get_neightbours(fish, visual_range=60)
            if fish.neighbours: #when there are neighbours
                neighbour_positions = []
                neighbour_velocities = []
                for neighbour in fish.neighbours:
                    neighbour_positions.append(neighbour.position)
                    neighbour_velocities.append(neighbour.velocity)
                    d = distance.euclidean(fish.current_position, neighbour.position)
                    if d < fish.nearest_distance:
                        fish.nearest_distance = d
                        fish.nearest_position = np.array(neighbour.position)
                fish.average_position = np.mean(neighbour_positions, axis=0)
                fish.average_velocity = np.mean(neighbour_velocities, axis=0)
                fish.position_difference = fish.average_position - fish.current_position
                fish.velocity_difference = fish.average_velocity - fish.current_velocity
                #alignment
                fish.alignment_vector = fish.position_difference
                fish.target_velocity += fish.alignment_vector
                #cohesion
                fish.cohesion_vector = fish.velocity_difference * 50
                fish.target_velocity += fish.cohesion_vector
                #separation
                fish.separation_vector = np.array([0,0])
                repulsion_range = 50
                if fish.nearest_distance < repulsion_range:
                    fish.separation_vector = fish.current_position-fish.nearest_position
                    fish.separation_vector = fish.separation_vector/np.linalg.norm(fish.separation_vector) #unit vector (direction)
                    fish.separation_vector *= 1/(fish.nearest_distance/repulsion_range+0.01)**2 #the closer the the nearest neighbour, the greater the repulsion
                    fish.target_velocity += fish.separation_vector
            else: #when there are no neighbours
                # fish.change_angle = random.gauss(mu=0, sigma=1) #random steering
                fish.target_velocity = np.random.normal(loc=0, scale=10, size=(2,)) #random velocity vector
            #when out of screen
            # margin = 25
            # if (not 0+margin<fish.center_x<self.window.width-margin) or (not 0+margin<fish.center_y<self.window.height-margin):
            #     fish.target_velocity = np.array([self.window.width/2, self.window.height/2]) - fish.current_position
            #come back from the otherside of the screen when out of bound
            fish.center_x %= self.window.width
            fish.center_y %= self.window.height

            # apply steering
            delta_angle = math.degrees(math.atan2(fish.target_velocity[1], fish.target_velocity[0]))  # in degrees; relative angle to the current angle
            fish.change_angle = delta_angle/180*15 #limit steering
            # apply movement based on steering and speed
            speed = math.log10(np.linalg.norm(fish.target_velocity))*2 #np.clip(np.linalg.norm(fish.target_velocity), a_min=0, a_max=1) #limit speed
            angle_radian = math.radians(fish.angle)
            fish.change_x = math.cos(angle_radian)*speed
            fish.change_y = math.sin(angle_radian)*speed


        # Call update on all sprites
        self.fish_list.update()
        self.player_list.update()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.fish_list)

        # Loop through each colliding sprite, remove it, and add to the
        # score.
        for fish in hit_list:
            fish.kill()
            self.score += 1
            self.window.total_score += 1

        # If we've collected all the games, then move to a "GAME_OVER"
        # state.
        if len(self.fish_list) == 0:
            game_over_view = GameOverView()
            game_over_view.time_taken = self.time_taken
            self.window.set_mouse_visible(True)
            self.window.show_view(game_over_view)

    def on_mouse_motion(self, x, y, _dx, _dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.F1:
            self.debug = not self.debug

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_taken = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        """
        Draw "Game over" across the screen.
        """
        arcade.draw_text("Game Over", self.window.width//2, self.window.height//10*7, arcade.color.WHITE, font_size=54, anchor_x="center")
        arcade.draw_text("Click to restart", self.window.width//2, self.window.height//10*3, arcade.color.WHITE, font_size=24, anchor_x="center")

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time taken: {time_taken_formatted}",
                         self.window.width//2,
                         self.window.height//10*5,
                         arcade.color.RED,
                         font_size=15,
                         anchor_x="center")

        output_total = f"Total Score: {self.window.total_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)

def main():
    window = arcade.Window(WIDTH, HEIGHT, "Swarm Intelligence")
    window.total_score = 0
    menu_view = GameView() #MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()