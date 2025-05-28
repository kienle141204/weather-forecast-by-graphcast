# import functools
# import haiku as hk
# import jax
# import xarray
# from google.cloud import storage
# from graphcast import (
#     autoregressive, casting, checkpoint, data_utils as du,
#     graphcast, normalization, rollout
# )

# class Predictor:
#     def __init__(self):
#         self.gcs_client = storage.Client.create_anonymous_client()
#         self.gcs_bucket = self.gcs_client.get_bucket('dm_graphcast')
#         self._load_model()
#         self._setup_model()

#     def _load_model(self):
#         """Load model weights and configuration"""
#         print('Connecting to dm_graphcast bucket...')
#         with self.gcs_bucket.blob('params/GraphCast_small - ERA5 1979-2015 - resolution 1.0 - pressure levels 13 - mesh 2to5 - precipitation input and output.npz').open('rb') as model:
#             ckpt = checkpoint.load(model, graphcast.CheckPoint)
#             self.params = ckpt.params
#             self.state = {}
#             self.model_config = ckpt.model_config
#             self.task_config = ckpt.task_config

#         # Load statistics files
#         print('Loading the diffs_stddev_by_level.nc file...')
#         blob = self.gcs_bucket.blob('stats/diffs_stddev_by_level.nc')
#         with blob.open('rb') as f:
#             self.diffs_stddev_by_level = xarray.load_dataset(f).compute()

#         print('Loading the mean_by_level.nc file...')
#         blob = self.gcs_bucket.blob('stats/mean_by_level.nc')
#         with blob.open('rb') as f:
#             self.mean_by_level = xarray.load_dataset(f).compute()

#         print('Loading the stddev_by_level.nc file...')
#         blob = self.gcs_bucket.blob('stats/stddev_by_level.nc')
#         with blob.open('rb') as f:
#             self.stddev_by_level = xarray.load_dataset(f).compute()

#     def _setup_model(self):
#         """Setup the GraphCast model with wrappers"""
#         def construct_wrapped_graphcast(model_config, task_config):
#             predictor = graphcast.GraphCast(model_config, task_config)
#             predictor = casting.Bfloat16Cast(predictor)
#             predictor = normalization.InputsAndResiduals(
#                 predictor,
#                 diffs_stddev_by_level=self.diffs_stddev_by_level,
#                 mean_by_level=self.mean_by_level,
#                 stddev_by_level=self.stddev_by_level
#             )
#             predictor = autoregressive.Predictor(predictor, gradient_checkpointing=True)
#             return predictor

#         @hk.transform_with_state
#         def run_forward(model_config, task_config, inputs, targets_template, forcings):
#             predictor = construct_wrapped_graphcast(model_config, task_config)
#             return predictor(inputs, targets_template=targets_template, forcings=forcings)

#         # Create partial functions with configs and params
#         def with_configs(fn):
#             return functools.partial(fn, model_config=self.model_config, task_config=self.task_config)

#         def with_params(fn):
#             return functools.partial(fn, params=self.params, state=self.state)

#         def drop_state(fn):
#             return lambda **kw: fn(**kw)[0]

#         # Create the final jitted forward function
#         self.run_forward_jitted = drop_state(
#             with_params(
#                 jax.jit(
#                     with_configs(run_forward.apply)
#                 )
#             )
#         )

#     def predict(self, inputs, targets, forcings) -> xarray.Dataset:
#         """Make predictions using the model"""
#         predictions = rollout.chunked_prediction(
#             self.run_forward_jitted,
#             rng=jax.random.PRNGKey(0),
#             inputs=inputs,
#             targets_template=targets,
#             forcings=forcings
#         )
#         return predictions 