#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
label: Score Segmentations

requirements:
- class: InlineJavascriptRequirement

inputs:
- id: parent_id
  type: string
- id: synapse_config
  type: File
- id: input_file
  type: File
- id: goldstandard
  type: File
# - id: mapping_file
#   type: File
- id: check_validation_finished
  type: boolean?

outputs:
- id: results
  type: File
  outputBinding:
    glob: results.json
- id: status
  type: string
  outputBinding:
    glob: results.json
    outputEval: $(JSON.parse(self[0].contents)['submission_status'])
    loadContents: true

baseCommand: score_seg.py
arguments:
- prefix: --parent_id
  valueFrom: $(inputs.parent_id)
- prefix: -s
  valueFrom: $(inputs.synapse_config.path)
- prefix: -p
  valueFrom: $(inputs.input_file.path)
- prefix: -g
  valueFrom: $(inputs.goldstandard.path)
- prefix: -m
#   valueFrom: $(inputs.mapping_file)
# - prefix: -o
  valueFrom: results.json

hints:
  DockerRequirement:
    dockerPull: docker.synapse.org/syn55249552/task2_validation_repo:v2

s:author:
- class: s:Person
  s:email: zanjal@usc.edu
  s:name: Shreyash Zanjal

s:codeRepository: https://github.com/LISA2024Challenge/LISA2024

$namespaces:
  s: https://schema.org/
