import random
import os

WORLD_FILE = '/home/thippe/my_robot/src/my_bot/worlds/ramps.world'

def generate_random_color():
    colors = ['Gazebo/Red', 'Gazebo/Blue', 'Gazebo/Green', 'Gazebo/Yellow', 'Gazebo/Purple', 'Gazebo/Orange', 'Gazebo/Turquoise', 'Gazebo/Grey']
    return random.choice(colors)

def generate_model_xml(idx):
    # Random position bounds (avoiding 0,0 where robot spawns)
    # Ramps are roughly 20x20.
    x = random.uniform(-8, 8)
    y = random.uniform(-8, 8)
    
    # Avoid center
    if -2 < x < 2 and -2 < y < 2:
        x += 4
        
    z = random.uniform(0.2, 1.5) # Some floating, some grounded? Heightmap implies ground is z=varies.
    # We'll set z to something safe + lift it. Actually with static=true it stays where put.
    # The heighmap varies. We should put them at z=1.0 or higher so they sit on terrain or float slightly.
    # Better: simple shapes.
    
    shape_type = random.choice(['box', 'cylinder', 'sphere'])
    
    color = generate_random_color()
    
    xml = f'''
    <model name="random_obstacle_{idx}">
      <pose>{x:.2f} {y:.2f} {z:.2f} 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
'''
    if shape_type == 'box':
        sx = random.uniform(0.2, 1.0)
        sy = random.uniform(0.2, 1.0)
        sz = random.uniform(0.2, 2.0)
        xml += f'''            <box>
              <size>{sx:.2f} {sy:.2f} {sz:.2f}</size>
            </box>
'''
    elif shape_type == 'cylinder':
        r = random.uniform(0.1, 0.5)
        l = random.uniform(0.5, 2.0)
        xml += f'''            <cylinder>
              <radius>{r:.2f}</radius>
              <length>{l:.2f}</length>
            </cylinder>
'''
    elif shape_type == 'sphere':
        r = random.uniform(0.2, 0.8)
        xml += f'''            <sphere>
              <radius>{r:.2f}</radius>
            </sphere>
'''

    xml += f'''          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
'''
    # Repeat geometry for visual
    if shape_type == 'box':
         xml += f'''            <box>
              <size>{sx:.2f} {sy:.2f} {sz:.2f}</size>
            </box>
'''
    elif shape_type == 'cylinder':
        xml += f'''            <cylinder>
              <radius>{r:.2f}</radius>
              <length>{l:.2f}</length>
            </cylinder>
'''
    elif shape_type == 'sphere':
        xml += f'''            <sphere>
              <radius>{r:.2f}</radius>
            </sphere>
'''
            
    xml += f'''          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>{color}</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
'''
    return xml

def main():
    with open(WORLD_FILE, 'r') as f:
        content = f.read()

    # Find the insertion point (before </world>)
    insert_pos = content.rfind('</world>')
    if insert_pos == -1:
        print("Error: Could not find </world> tag")
        return

    new_models = "\n    <!-- GENERATED RANDOM OBSTACLES -->\n"
    for i in range(30):
        new_models += generate_model_xml(i)
        
    new_content = content[:insert_pos] + new_models + content[insert_pos:]
    
    with open(WORLD_FILE, 'w') as f:
        f.write(new_content)
        
    print("Added 30 random obstacles to rams.world")

if __name__ == '__main__':
    main()
