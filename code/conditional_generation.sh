#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:/workspace/code"
weight_energy=1
gpt_size='base'
data_type='sentiment' 
name='LM/art_data/v8_bertus_base_VAE0.9_fx84_64_b16_e50_d0.9'


latent_size=64


eval_batch=50
n_classes=2
if [ $data_type == 'sentiment' ]
then
  cls_step=1
elif [ $data_type == 'tense' ]
then
  cls_step=4
  n_classes=3
  elif [ $data_type == 'formality' ]
then
  cls_step=33
  n_classes=2
elif [ $data_type == 'amazon' ]
then
  cls_step=2
  if [ $gpt_size == 'base' ]; then
    weight_energy=2
  fi
fi
cls_step=$1
att_val_list=$2

cuda='2' #$3

echo "cls: $cls_step"

if [ $gpt_size == 'large' ]; then
  gpt_path=gpt2-large
elif [ $gpt_size == 'base' ]; then
  gpt_path=gpt2
else
  echo "False"
fi

CUDA_VISIBLE_DEVICES=$cuda python examples/big_ae/conditional_generation.py \
    --output_dir=../ckpts/$name  \
    --encoder_model_type=bertu \
    --encoder_model_name_or_path=prajjwal1/bert-small \
    --decoder_model_type=gpt2 \
    --decoder_model_name_or_path=$gpt_path \
    --do_train \
    --do_eval \
    --fb_mode 1 \
    --train_data_file=$TRAIN_FILE \
    --eval_data_file=$TEST_FILE \
    --overwrite_output_dir \
    --per_gpu_train_batch_size=$eval_batch \
    --per_gpu_eval_batch_size=$eval_batch \
    --block_size 50 \
    --length_weighted_loss \
    --latent_size $latent_size \
    --evaluate_during_training \
    --use_pretrained_model \
    --use_pretrained_vae \
    --checkpoint_dir  ../ckpts/$name --gloabl_step_eval 1 \
    --gan_dir ../ckpts/$name/checkpoint-gan-accommodate \
    --cls_dir ../ckpts/$name/checkpoint-cls- \
    --n_classes $n_classes --cls_step $cls_step --att_val_list $att_val_list --sampling_num 150 \
    --data_type $data_type --weight_energy $weight_energy 
#    --load_weight_from_json ../output_home/LM/$data/$name/sample/weight_test.json

#

#sleep 0.05

#cd ..
#python eval_sampling.py --data $data --path $name --data_type $data_type
#cd code
