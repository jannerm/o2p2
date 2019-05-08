# Object-Oriented Prediction and Planning

Code for generating data used in the paper [Reasoning About Physical Interactions with Object-Oriented Prediction and Planning](https://people.eecs.berkeley.edu/~janner/o2p2/).

## Setup
Download [MuJoCo 1.5](https://www.roboti.us/index.html) and run `pip install -r requirements.txt` with Python 3.6. 

## Data generation
See `mujoco/generate.py` for an example. This should generate image sequences like the following:

<br>
<p float="center">
  <img src="https://drive.google.com/uc?export=view&id=1iJDYIdx99qdcwTIsMM1Q7n0I3_j0DiXY" width="19%">
  <img src="https://drive.google.com/uc?export=view&id=1ojpswJna-mO0jJsbUAVkm5ZfBhDZVyXI" width="19%">
  <img src="https://drive.google.com/uc?export=view&id=1vIGQwLQuXOLLNUv8GyiCmv9edAiqWNxb" width="19%">
  <img src="https://drive.google.com/uc?export=view&id=1jOLp9agc-WF1oi9AiiU16VvyPf4A9Ipw" width="19%">
  <img src="https://drive.google.com/uc?export=view&id=1TLUQo3ekl9Err_Mi_7hK77Q2bAUwlTwG" width="19%">
</p>

Note that in the paper, we only used the first and final image instead of the full sequence. To only render these images, set `render_freq` equal to `drop_steps_max`:
```
python mujoco/generate.py --drop_steps_max 1000 --render_freq 1000 \
    --num_images 10 --img_dim 64 --min_objects 2 --max_objects 4 --output_path rendered/initial_final/
```

If you would like to add a new shape, just drop the stl file in `assets/stl` and add its filename (without the stl extension) to the list of [polygons](mujoco/generate.py#L47).