"""

Hydra builder function for DMPO agent


"""
from tonic.torch.agents.dmpo import models, normalizers, updaters
from tonic.torch.agents.diffusion_utils.utils import IdentityEncoder, IdentityTorso
from tonic import replays 
import torch.nn
import torch

def build_model(cfg):
    head_cfg = cfg["actor"]["head"]
    actor_head = models.DiffusionPolicyHead(
        device=head_cfg["device"],
        num_diffusion_steps=head_cfg["num_diffusion_steps"],
        hidden_dim=head_cfg["hidden_dim"],
        n_hidden=head_cfg["n_hidden"],
        n_blocks=head_cfg["n_blocks"],
        sigma_data=head_cfg["sigma_data"],
        sampler_type=head_cfg["sampler_type"],
        model_type=head_cfg["model_type"]
    )


    if cfg["actor"]["encoder"]["name"] == "IdentityEncoder":
        actor_encoder = IdentityEncoder()


    if cfg["actor"]["torso"]["name"] == "IdentityTorso":
        actor_torso = IdentityTorso()


    actor = models.DiffusionActor(
        encoder=actor_encoder,
        torso=actor_torso,
        head=actor_head
    )

    # 3) Build critic
    critic_cfg = cfg["critic"]
    # Encoder
    if critic_cfg["encoder"]["name"] == "ObservationActionEncoder":
        critic_encoder = models.ObservationActionEncoder()

    # Torso
    torso_cfg = critic_cfg["torso"]
    if torso_cfg["name"] == "MLP":
        hidden_layers = tuple(torso_cfg["hidden_layers"])
        activation = getattr(torch.nn, torso_cfg["activation"])
        critic_torso = models.MLP(hidden_layers, activation)

    # Head
    if critic_cfg["head"]["name"] == "ValueHead":
        critic_head = models.ValueHead()
    
    critic_device = critic_cfg["device"]

    critic = models.Critic(
        encoder=critic_encoder,
        torso=critic_torso,
        head=critic_head,
        device= critic_device
    )

    # 4) Observation normalizer
    obs_norm_cfg = cfg["observation_normalizer"]
    if obs_norm_cfg and obs_norm_cfg["name"] == "MeanStd":
        observation_normalizer = normalizers.MeanStd()
    else:
        observation_normalizer = None

    # 5) State Dependent Temperature        
    temp_cfg = cfg["temperature"]       
    temperature = models.Temperature(IdentityEncoder(),temp_cfg["hidden_dim"],temp_cfg["n_hidden"],temp_cfg["device"])

    return models.DiffusionActorCriticWithTargets(
        actor=actor,
        critic=critic,
        temperature=temperature,
        observation_normalizer=observation_normalizer,
        actor_squash=cfg["actor_squash"],
        action_scale=cfg["action_scale"],
        target_coeff=cfg.get("target_coeff", 0.005)
    )


def build_actor_updater(cfg):
   
    actor_cfg = cfg
    
    if actor_cfg["name"] == "DiffusionMaximumAPosterioriPolicyOptimization":

        optim_cfg = actor_cfg["optimizer"]
        if optim_cfg["name"] == "Adam":
            learning_rate = optim_cfg["learning_rate"]
            actor_optimizer = lambda params: torch.optim.Adam(params, lr=learning_rate)

            dual_learning_rate = optim_cfg["dual_learning_rate"]
            dual_optimizer = lambda params: torch.optim.Adam(params, lr=dual_learning_rate)

        

        return updaters.DiffusionMaximumAPosterioriPolicyOptimization(
            num_samples=actor_cfg["num_samples"],
            epsilon=actor_cfg["epsilon"],
            epsilon_penalty=actor_cfg["epsilon_penalty"],
            epsilon_mean=actor_cfg["epsilon_mean"],
            epsilon_std=actor_cfg["epsilon_std"],
            initial_log_temperature=actor_cfg["initial_log_temperature"],
            initial_log_alpha_mean=actor_cfg["initial_log_alpha_mean"],
            initial_log_alpha_std=actor_cfg["initial_log_alpha_std"],
            min_log_dual=actor_cfg["min_log_dual"],
            per_dim_constraining=actor_cfg["per_dim_constraining"],
            action_penalization=actor_cfg["action_penalization"],
            actor_optimizer=actor_optimizer,
            dual_optimizer=dual_optimizer,
            actor_gradient_clip=actor_cfg["actor_gradient_clip"],
            dual_gradient_clip=actor_cfg["dual_gradient_clip"],
            temperature_state=actor_cfg["temperature_state"]
        )
    
    raise ValueError(f"Unsupported actor updater: {actor_cfg['name']}")


def build_critic_updater(cfg):

    critic_cfg = cfg
    
    if critic_cfg["name"] == "DiffusionExpectedSARSA":
        # Get optimizer
        optim_cfg = critic_cfg["optimizer"]
        if optim_cfg["name"] == "Adam":
            learning_rate = optim_cfg["learning_rate"]
            critic_optimizer = lambda params: torch.optim.Adam(params, lr=learning_rate)
        # Add more optimizers as needed
        
        # Create the updater
        return updaters.DiffusionExpectedSARSA(
            num_samples=critic_cfg["num_samples"],
            optimizer=critic_optimizer,
            gradient_clip=critic_cfg["gradient_clip"]
        )
    
    raise ValueError(f"Unsupported critic updater: {critic_cfg['name']}")



def build_replay_updater(cfg):

    if cfg["name"] == "Buffer":
        size = cfg["size"]
        batch_size = cfg["batch_size"]
        discount_factor = cfg["discount_factor"]
        steps_before_batches = cfg["steps_before_batches"]
        return_steps = cfg["return_steps"]
        steps_between_batches = cfg["steps_between_batches"] 
        
        return replays.Buffer(size=size, batch_size=batch_size,\
            discount_factor=discount_factor, steps_before_batches=steps_before_batches, \
                return_steps=return_steps,  steps_between_batches=steps_between_batches )        
         
    raise ValueError(f"Unsupported Replay updater: {cfg['name']}")
