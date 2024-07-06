#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: ExpressionTool
label: Get goldstandard based on task number

requirements:
- class: InlineJavascriptRequirement

inputs:
- id: queue
  type: string

outputs:
- id: synid
  type: string
- id: label
  type: string

expression: |

  ${
    if (inputs.queue == "9615562") {
      return {
        synid: "syn61630515",
        label: "Task 1 Evaluation"
      };
    } else if (inputs.queue == "9615605") {
      return {
        synid: "syn61630515",
        label: "Task 2 Evaluation"
      };
    } else {
      throw 'invalid queue';
    }
  }