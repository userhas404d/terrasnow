// Table: sc_cat_item
// application: Global
// Active: true
// Advanced: true
// When to run:
//   When: before
//   Order: 100
//   Insert: true
//   Update: true
//   filter conditions:
//     Catalogs > contains: 'Terraform Resources' << this is a table selector
//     & Active > changes
// Actions: blank
// Advanced:
//   Condition: 'current.active == false'
//   Script:

  (function executeRule(current, previous /*null when async*/) {

  	//workflow context sys_id

  var wf = new Workflow();
  var wfname = 'terraform catalog item deletion';
  var wfId = wf.getWorkflowFromName(wfname);
  gs.log('BR testing: ' + current.active );
  gs.log('workflow sysId: ' + wfId);
  var context = wf.startFlow(wfId, null, wfname, null); wt.startflow(id, current, current.update);

  })(current, previous);
