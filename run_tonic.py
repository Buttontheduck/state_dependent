import hydra
from omegaconf import OmegaConf
from tonic.train import train  # updated import
import wandb, yaml




@hydra.main(config_path="/home/ka/ka_anthropomatik/ka_ln2554/state_dependent/configs", config_name="exp15")
def main(cfg):
    print(OmegaConf.to_yaml(cfg))
    
    raw_config = OmegaConf.to_container(cfg, resolve=True)
    project_config = wandb.helper.parse_config(raw_config)   

    project_name = raw_config['wandb_config']['wandb_config']['project']
    run_name = raw_config['wandb_config']['wandb_config']['name']
    group_name = raw_config['wandb_config']['wandb_config']['group']
    wb_note = raw_config['wandb_config']['wandb_config']['notes']
    
    wandb.init(project=project_name, name=run_name, notes=wb_note, group = group_name, config=project_config)


    train(**cfg)

if __name__ == "__main__":
    main()