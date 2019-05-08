import os
import argparse
import pickle
import math
import random
import tqdm
import pdb

import mujoco_py as mjc
import matplotlib.pyplot as plt

from XML import XML
from logger import Logger
import contacts
import utils

parser = argparse.ArgumentParser()
## stuff you might want to edit
parser.add_argument('--start', default=0, type=int, 
        help='starting index (useful if rendering in parallel jobs)')
parser.add_argument('--num_images', default=5, type=int,
        help='total number of images to render')
parser.add_argument('--img_dim', default=256, type=int,
        help='image dimension')
parser.add_argument('--output_path', default='rendered/test/', type=str,
        help='path to save images')

parser.add_argument('--drop_steps_max', default=500, type=int,
        help='max number of steps simulating dropped object')
parser.add_argument('--render_freq', default=25, type=int,
        help='frequency of image saves in drop simulation')

parser.add_argument('--min_objects', default=4, type=int,
        help='min number of objects *starting on the ground*')
parser.add_argument('--max_objects', default=4, type=int,
        help='max number of objects *starting on the ground*')

## stuff you probably don't need to edit
parser.add_argument('--settle_steps_min', default=2000, type=int,
        help='min number of steps simulating ground objects to rest')
parser.add_argument('--settle_steps_max', default=2000, type=int,
        help='max number of steps simulating ground objects to rest')
parser.add_argument('--save_images', default=True, type=bool,
        help='if true, saves images as png (alongside pickle files)')
args = parser.parse_args()


polygons = ['cube', 'horizontal_rectangle', 'tetrahedron'] 

num_objects = range(args.min_objects, args.max_objects + 1)

## bounds for objects that start on the ground plane
settle_bounds = {  
            'pos':   [ [-.5, .5], [-.5, 0], [1, 2] ],
            'hsv': [ [0, 1], [0.5, 1], [0.5, 1] ],
            'scale': [ [0.4, 0.4] ],
            'force': [ [0, 0], [0, 0], [0, 0] ]
          }

## bounds for the object to be dropped
drop_bounds = {  
            'pos':   [ [-1.75, 1.75], [-.5, 0], [0, 3] ],
          }  

## folder with object meshes
asset_path = os.path.join(os.getcwd(), 'assets/stl/')

utils.mkdir(args.output_path)

metadata = {'polygons': polygons, 'max_steps': args.drop_steps_max, 
            'min_objects': min(num_objects), 
            'max_objects': max(num_objects)}
pickle.dump( metadata, open(os.path.join(args.output_path, 'metadata.p'), 'wb') )

num_images_per_scene = math.ceil(args.drop_steps_max / args.render_freq)
end = args.start + args.num_images
for img_num in tqdm.tqdm( range(args.start, end) ):

    sim, xml, drop_name = contacts.sample_settled(asset_path, num_objects, polygons, settle_bounds)
    logger = Logger(xml, sim, steps = num_images_per_scene, img_dim = args.img_dim )
    
    ## drop all objects except [ drop_name ]
    logger.settle_sim(drop_name, args.settle_steps_min, args.settle_steps_max)

    ## filter scenes in which objects are intersecting
    ## because it makes the physics unpredictable
    overlapping = True
    while overlapping:

        ## get position for drop block
        if random.uniform(0, 1) < 0.5 and len(xml.meshes) > 1:
            ## some hard-coded messiness
            ## to drop a block directly on top
            ## of an existnig block half of the time
            mesh = random.choice(xml.meshes)
            pos = [float(p) for p in mesh['pos'].split(' ')]
            pos[2] += random.uniform(.4, .8)
        else:
            ## drop on random position
            pos = utils.uniform(*drop_bounds['pos'])

        ## get orientation for drop block
        if 'horizontal' in drop_name:
            axangle = [1,0,0,0]
        else:
            axis = [0,0,1]
            axangle  = utils.random_axangle(axis=axis)

        ## position and orient the block
        logger.position_body(drop_name, pos, axangle)

        ## check whether there are any block intersections
        overlapping = contacts.is_overlapping(sim, drop_name)

    for i in range(args.drop_steps_max):
        ## log every [ render_freq ] steps
        if i % args.render_freq == 0:
            logger.log(i//args.render_freq)
        ## simulate one timestep
        sim.step()
    
    data, images, masks = logger.get_logs()

    if args.save_images:
        for timestep in range( images.shape[0] ):
            plt.imsave( os.path.join(args.output_path, '{}_{}.png'.format(img_num, timestep)), images[timestep] / 255. )

    config_path  = os.path.join( args.output_path, '{}.p'.format(img_num) )

    config = {'data': data, 'images': images, 'masks': masks, 'drop_name': drop_name}

    pickle.dump( config, open(config_path, 'wb') )












