#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
label: Validate segmentation submission

requirements:
- class: InlineJavascriptRequirement

inputs:
- id: input_file
  type: File
- id: goldstandard
  type: File
- id: entity_type
  type: string
# - id: pred_pattern
#   type: string
# - id: gold_pattern
#   type: string

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
- id: invalid_reasons
  type: string
  outputBinding:
    glob: results.json
    outputEval: $(JSON.parse(self[0].contents)['submission_errors'])
    loadContents: true

baseCommand: validate_seg.py
arguments:
- prefix: -p
  valueFrom: $(inputs.input_file)
- prefix: -g
  valueFrom: $(inputs.goldstandard.path)
- prefix: -e
  valueFrom: $(inputs.entity_type)
- prefix: -o
  valueFrom: results.json
# - prefix: --pred_pattern
#   valueFrom: $(inputs.pred_pattern)
# - prefix: --gold_pattern
#   valueFrom: $(inputs.gold_pattern)

hints:
  DockerRequirement:
    dockerPull: docker.synapse.org/syn55249552/task2_validation_repo:v3

s:author:
- class: s:Person
  s:email: zanjal@usc.edu
  s:name: Shreyash Zanjal

s:codeRepository: https://github.com/LISA2024Challenge/LISA2024


$namespaces:
  s: https://schema.org/
