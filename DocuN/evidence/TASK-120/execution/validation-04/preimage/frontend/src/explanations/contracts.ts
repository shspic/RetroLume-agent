export type HtmlParent = {kind:"learning";operation_id:string;payload_sha256:string;segment_index:number} |
  {kind:"teaching";record_id:string;body_sha256:string;point_id:string|null};
export type HtmlInput = {id:string;kind:"number"|"range"|"integer";label:string;description:string;min:string;max:string;step:string;default:string};
export type HtmlDescription = {schema:"interactive_description.v1";title:string;concept:string;inputs:HtmlInput[];
  actions:{id:string;kind:"reset";label:string}[];views:{id:string;kind:string;label:string;unit?:string}[];
  calculation_notes:{formula:string;domain:string;error:string;samples:{input:string;expected:string}[];citations:string[]}[];limitations:string[]};
export type HtmlCommand = {business_key:string;parent:HtmlParent;focus:string;expected_config_sha256:string;confirmed:true};
export type HtmlReceipt = {outbound_approval?:import('../activities/retrieval-api').QApproval|null;business_key:string;operation_id:string;status:string;terminal_disposition:string|null;error_code:string|null;
  artifact_id:string|null;artifact_sha256:string|null;accepted_input:HtmlCommand;read_status:string};
export type HtmlArtifact = {artifact_id:string;business_key:string;artifact_sha256:string;renderer_sha256:string;
  description:HtmlDescription;parent:HtmlParent;citations:{citation_id:string;title:string;text:string;source_id:string;version_id:string}[]};
export type HtmlPreview = {preview_id:string;artifact_id:string;artifact_sha256:string;generation:number;owner_id:string;boot_id:string;
  state:string;eligible:boolean;deadline_at:string;reserve_seconds:number;elapsed_seconds:number|null;starts_used:number;settled_seconds:number;reserved_seconds:number};
export type HtmlAck = {seq:number;preview_id:string;generation:number;artifact_sha256:string;accepted:boolean;error_code:string|null;
  readouts:{id:string;value:string;unit:string}[];steps:number;input_values:Record<string,string>};
export type HtmlCapabilities = {available:boolean;reason:string|null;config_sha256:string|null;max_starts:number;max_seconds:number;max_window:number;
  budget:{starts_used:number;settled_seconds:number;reserved_seconds:number}|null};
export type HtmlEvent = {type:"set_number";control_id:string;value:string}|{type:"activate";action_id:string};
