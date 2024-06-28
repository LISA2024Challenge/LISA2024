# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 12:47:21 2024

@author: rrouhi
"""

#!/usr/bin/env python3
"""Scoring script for hippocampus segmentation.

Run computation and return:
  - Dice Similarity Coefficient (DSC)
  - Hausdorff Distance (HD) and 95 Hausdorff Distance (95HD)
  - Average Symmetric Surface Distance (ASSD)
  - Relative Volume Error (RVE)
  - Metrics for left and right hippocampus separately and their averages
"""
import os
import argparse
import json
import pandas as pd
import synapseclient
from evalutils.io import SimpleITKLoader
import SimpleITK as sitk
import numpy as np
from surface_distance.metrics import compute_surface_distances, compute_average_surface_distance, compute_dice_coefficient, compute_robust_hausdorff
import utils
from utils import inspect_zip

def get_args():
    """Set up command-line interface and get arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent_id", type=str, required=True)
    parser.add_argument("-s", "--synapse_config", type=str, default="/.synapseConfig")
    parser.add_argument("-p", "--predictions_file", type=str, default="LISA_LF_SEG_predictions.zip")
    parser.add_argument("-g", "--goldstandard_file", type=str, default="LISA_LF_SEG_goldstandard.zip")
    parser.add_argument("-o", "--output", type=str, default="results.json")
    return parser.parse_args()

def calculate_metrics(gt_file, pred_file, voxel_sz):
    """Calculate metrics for segmentation."""
    
    gt_array = sitk.GetArrayFromImage(gt_file)
    pred_array = sitk.GetArrayFromImage(pred_file)
    
    gt_array_L = (gt_array == 1)
    pred_array_L = (pred_array == 1)
    
    gt_array_R = (gt_array == 2)
    pred_array_R = (pred_array == 2)
    
    dsc_value_L = compute_dice_coefficient(gt_array_L, pred_array_L)
    surface_dist_L = compute_surface_distances(pred_array_L, gt_array_L, spacing_mm=voxel_sz)
    hd_value_L = compute_robust_hausdorff(surface_dist_L, 100)
    hd95_value_L = compute_robust_hausdorff(surface_dist_L, 95)
    mean_surface_dist_L = compute_average_surface_distance(surface_dist_L)
    assd_value_L = np.mean(mean_surface_dist_L)
    gt_volume_L = np.sum(gt_array_L)
    pred_volume_L = np.sum(pred_array_L)
    rve_value_L = abs((pred_volume_L - gt_volume_L) / gt_volume_L)

    dsc_value_R = compute_dice_coefficient(gt_array_R, pred_array_R)
    surface_dist_R = compute_surface_distances(pred_array_R, gt_array_R, spacing_mm=voxel_sz)
    hd_value_R = compute_robust_hausdorff(surface_dist_R, 100)
    hd95_value_R = compute_robust_hausdorff(surface_dist_R, 95)
    mean_surface_dist_R = compute_average_surface_distance(surface_dist_R)
    assd_value_R = np.mean(mean_surface_dist_R)
    gt_volume_R = np.sum(gt_array_R)
    pred_volume_R = np.sum(pred_array)
    rve_value_R = abs((pred_volume_R - gt_volume_R) / gt_volume_R)

    return round(dsc_value_L,3), round(hd_value_L,3), round(hd95_value_L,3), round(assd_value_L,3), round(rve_value_L,3), round(dsc_value_R,3), round(hd_value_R,3), round(hd95_value_R,3), round(assd_value_R,3), round(rve_value_R)

def score_seg(gold, pred_lst, label):
    """Compute and return scores for each scan."""
    scores = []
    voxel_sz = [1, 1, 1]
    script_dir = os.path.dirname(os.path.realpath(__file__))
    ind=0
    for pred in pred_lst:
        # scan_id = pred[-12:-7] ### to be modified
        # gold = os.path.join(parent, f"{label}-{scan_id}-seg.nii.gz")
        predicted_path = os.path.join(script_dir,pred)
        ground_truth_path = os.path.join(script_dir,gold[ind])
        loader = SimpleITKLoader()
        gt = loader.load_image(ground_truth_path)
        pred = loader.load_image(predicted_path)

        caster = sitk.CastImageFilter()
        caster.SetOutputPixelType(sitk.sitkFloat32)
        caster.SetNumberOfThreads(1)

        gold_im = caster.Execute(gt)
        pred_im = caster.Execute(pred)
        
        dsc_L, hd_L, hd95_L, assd_L, rve_L, dsc_R, hd_R, hd95_R, assd_R, rve_R = calculate_metrics(gold_im, pred_im, voxel_sz)
        
        dsc_avg = round((dsc_L + dsc_R)/2,3)
        hd_avg = round((hd_L + hd_R)/2,3)
        hd95_avg = round((hd95_L + hd95_R)/2,3)
        assd_avg = round((assd_L + assd_R)/2,3)
        rve_avg = round((rve_L + rve_R)/2,3)
    
        
        parts = gold[ind].split('_')

        # Reconstruct the desired part of the name of gold files
        substring = '_'.join(parts[6:])


        scan_scores = {
            'scan_id': substring,
            'DSC_L': dsc_L,
            'DSC_R': dsc_R,
            'DSC_Avg': dsc_avg,
            'HD_L': hd_L,
            'HD_R': hd_R,
            'HD_Avg': hd_avg,
            'HD95_L': hd95_L,
            'HD95_R': hd95_R,
            'HD95_Avg': hd95_avg,
            'ASSD_L': assd_L,
            'ASSD_R': assd_R,
            'ASSD_Avg': assd_avg,
            'RVE_L': rve_L,
            'RVE_R': rve_R,
            'RVE_Avg': rve_avg
        }

        scores.append(scan_scores)
        
        ind +=1
        
    return pd.DataFrame(scores).sort_values(by="scan_id")

def main():
    """Main function."""
    args = get_args()
    preds = utils.inspect_zip(args.predictions_file)
    golds = utils.inspect_zip(args.goldstandard_file)

    # dir_name = os.path.split(golds[0])[0]######### to be modified 
    results = score_seg(golds, preds, label="hippocampus")

    # Get number of segmentations predicted by participant, as well as descriptive statistics for results.
    cases_evaluated = len(results.index)
    metrics_summary = (results.describe()
                       .rename(index={'25%': "25quantile", '50%': "median", '75%': "75quantile"})
                       .drop(["count", "min", "max"]))
    results = pd.concat([results, metrics_summary])
    
    #add the average of the metrics
    # List of columns to calculate averages for
    numeric_columns = results.select_dtypes(include='number').columns
    
    # Calculate averages
    averages = results[numeric_columns].mean()
    std_devs = results[numeric_columns].std()
    # Append averages as a new row
    # Format averages and standard deviations as strings "avg ± std"
    average_strings = [f"{avg:.2f}±{std:.2f}" for avg, std in zip(averages, std_devs)]
    
    # Append the formatted string to the "Average" row in the DataFrame
    results.loc[len(results)] = ['Average'] + average_strings

    # CSV file of scores for all scans.
    results.to_csv("all_scores_seg.csv", index=False, encoding="cp1252")
    syn = synapseclient.Synapse(configPath=args.synapse_config)
    syn.login(silent=True)
    csv = synapseclient.File("all_scores_seg.csv", parent=args.parent_id)
    csv = syn.store(csv)

    #Results file for annotations.
    with open(args.output, "w") as out:
        res_dict = {**results.loc["mean"],
                    "cases_evaluated": cases_evaluated,
                    "submission_scores": csv.id,
                    "submission_status": "SCORED"}
        res_dict = {k: v for k, v in res_dict.items() if not pd.isna(v)}
        out.write(json.dumps(res_dict))
    

if __name__ == "__main__":
    main()
