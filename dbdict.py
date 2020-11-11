#==============================================================================
#
# Name: dbdict.py
#
# Purpose: Python module containing production database dictionary.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

# Global database dictionary.
#
# The structure of the dictionary is as follows.
#
#{ table1: [column1, column2, ...],
#  table2: [column1, column2, ...],
#  ...}
#
# Each column is a 5-tuples consisting of the following elements.
#
# 1.  Database column name (if any).
# 2.  XML element name (if any).
# 3.  Database type + constraints.
# 4.  Array flag (0 or 1).
# 5.  Description.
#
# Notes.
#
# 1.  Foreign key constraints include item 3, but no column name.
# 2.  If the array flag is true, this column is an integer foreign key that joins with another table.
#

# Tables in creation order:

tables = ['projects', 'stages', 'substages', 'strings']

# Database dictionary.

databaseDict = {'projects': [('id', '', 'INT NOT NULL PRIMARY KEY AUTO_INCREMENT', 0, 'Project ID'),
                             ('name', '',  'VARCHAR(100) NOT NULL', 0, 'Project name'),
                             ('num_events', 'numevents', 'INT', 0, 'Number of events'),
                             ('num_jobs', 'numjobs', 'INT', 0, 'number of jobs'),
                             ('max_files_per_job', 'maxfilesperjob', 'INT', 0, 'Maximum files per job'),
                             ('os', 'os', 'VARCHAR(1000)', 0, 'OS'),
                             ('resource', 'resource', 'VARCHAR(1000)', 0, 'Jobsub resource'),
                             ('role', 'role', 'VARCHAR(1000)', 0, 'Role'),
                             ('lines_', 'lines', 'VARCHAR(1000)', 0, 'Jobsub lines'),
                             ('server', 'server', 'VARCHAR(1000)', 0, 'Jobsub server'),
                             ('site', 'site', 'VARCHAR(1000)', 0, 'Site'),
                             ('blacklist', 'blacklist', 'VARCHAR(1000)', 0, 'Blacklist'),
                             ('cpu', 'cpu', 'INT', 0, 'Maximum CPU'),
                             ('disk', 'disk', 'VARCHAR(1000)', 0, 'Maximum disk'),
                             ('memory', 'memory', 'INT', 0, 'Maximum memory'),
                             ('merge', 'merge', 'VARCHAR(1000)', 0, 'Merge program/flag'),
                             ('anamerge', 'anamerge', 'VARCHAR(1000)', 0, 'Analyzie merge flag'),
                             ('release_tag', 'larsoft/tag', 'VARCHAR(1000)', 0, 'Release version'),
                             ('release_qual', 'larsoft/qual', 'VARCHAR(1000)', 0, 'Release qualifier'),
                             ('version', 'version', 'VARCHAR(1000)', 0, 'Sam version'),
                             ('local_release_tar', 'larsoft/local', 'VARCHAR(1000)', 0, 'Local release tarball'),
                             ('poms_login_setup', 'poms/loginsetup', 'VARCHAR(1000)', 0, 'POMS login/stup'),
                             ('poms_job_type', 'poms/jobtype', 'VARCHAR(1000)', 0, 'POMS job type'),
                             ('poms_campaign', 'poms/campaign', 'VARCHAR(1000)', 0, 'POMS campaign'),
                             ('file_type', 'filetype', 'VARCHAR(1000)', 0, 'Sam file type'),
                             ('run_type', 'runtype', 'VARCHAR(1000)', 0, 'Sam run type'),
                             ('run_number', 'runnumber', 'INT', 0, 'Run number'),
                             ('script', 'script', 'VARCHAR(1000)', 0, 'Batch script'),
                             ('validate_on_worker', 'check', 'INT', 0, 'Validate on worker flag'),
                             ('copy_to_fts', 'copy', 'INT', 0, 'Copy to FTS flag'),
                             ('start_script', 'startscript', 'VARCHAR(1000)', 0, 'Batch start script'),
                             ('stop_script', 'stopscript', 'VARCHAR(1000)', 0, 'Batch stop script'),
                             ('ups', 'ups', 'INT', 1, 'Top level ups products'),
                             ('fcldir', 'fcldir', 'INT', 1, 'Fcl search path')],
                'stages': [('id', '', 'INT NOT NULL PRIMARY KEY AUTO_INCREMENT', 0, 'Stage ID'),
                           ('name', '', 'VARCHAR(1000) NOT NULL', 0, 'Stage name'),
                           ('project_id', '', 'INT NOT NULL', 0, 'Parent project ID'),
                           ('seqnum', '', 'INT', 0, 'Sequence number'),
                           ('batchname', 'batchname', 'VARCHAR(1000)', 0, 'Batch job name'),
                           ('poms_stage', 'pomsstage', 'VARCHAR(1000)', 0, 'POMS stage'),
                           ('outdir', 'outdir', 'VARCHAR(1000)', 0, 'Output directory'),
                           ('logdir', 'logdir', 'VARCHAR(1000)', 0, 'Log file directory'),
                           ('workdir', 'workdir', 'VARCHAR(1000)', 0, 'Work directory'),
                           ('bookdir', 'bookdir', 'VARCHAR(1000)', 0, 'Bookkeeping directory'),
                           ('dirlevels', 'dirlevels', 'INT', 0, 'Intermediate directory levels'),
                           ('dirsize', 'dirsize', 'INT', 0, 'Intermediate directory size'),
                           ('inputdef', 'inputdef', 'VARCHAR(1000)', 0, 'Input dataset'),
                           ('recurdef', 'recurdef', 'VARCHAR(1000)', 0, 'Recursive input dataset'),
                           ('ana', 'ana', 'INT', 0, 'Analysis flag'),
                           ('recur', 'recur', 'INT', 0, 'Recursive flag'),
                           ('recurtype', 'recurtype', 'VARCHAR(1000)', 0, 'Recursion type'),
                           ('recurlimit', 'recurlimit', 'INT', 0, 'Recursive file limit'),
                           ('filelistdef', 'filelistdef', 'INT', 0, 'File list definition flag'),
                           ('prestart', 'prestart', 'INT', 0, 'Prestart sam project flag'),
                           ('activebase', 'activebase', 'VARCHAR(1000)', 0, 'Active project base'),
                           ('dropboxwait', 'dropboxwait', 'DOUBLE', 0, 'Dropbox waiting period'),
                           ('prestagefraction', 'prestagefraction', 'DOUBLE', 0, 'Prestage fraction'),
                           ('maxfluxfilemb', 'maxfluxfilemb', 'INT', 0, 'Maximum flux file MB'),
                           ('num_jobs', 'numjobs', 'INT', 0, 'Number of jobs'),
                           ('num_events', 'numevents', 'INT', 0, 'Number of events'),
                           ('max_files_per_job', 'maxfilesperjob', 'INT', 0, 'Maximum files per job'),
                           ('target_size', 'targetsize', 'INT', 0, 'Target file size'),
                           ('defname', 'defname', 'VARCHAR(1000)', 0, 'Output dataset'),
                           ('ana_defname', 'ana_defname', 'VARCHAR(1000)', 0, 'Output analysis dataset'),
                           ('data_tier', 'datatier', 'VARCHAR(1000)', 0, 'Data tier'),
                           ('ana_data_tier', 'anadatatier', 'VARCHAR(1000)', 0, 'Analysis data tier'),
                           ('submit_script', 'submitscript', 'VARCHAR(1000)', 0, 'Submit script'),
                           ('merge', 'merge', 'VARCHAR(1000)', 0, 'Merge program/flag'),
                           ('anamerge', 'anamerge', 'VARCHAR(1000)', 0, 'Analysis merge flag'),
                           ('resource', 'resource', 'VARCHAR(1000)', 0, 'Jobsub resource'),
                           ('lines_', 'lines', 'VARCHAR(1000)', 0, 'Jobsub lines'),
                           ('site', 'site', 'VARCHAR(1000)', 0, 'Jobsub site'),
                           ('blacklist', 'blacklist', 'VARCHAR(1000)', 0, 'Jobsub blacklist'),
                           ('cpu', 'cpu', 'INT', 0, 'Maximum cpu'),
                           ('disk', 'disk', 'VARCHAR(1000)', 0, 'Maximum disk'),
                           ('memory', 'memory', 'INT', 0, 'Maximum memory'),
                           ('TFileName', 'TFileName', 'VARCHAR(1000)', 0, 'TFileName'),
                           ('jobsub', 'jobsub', 'VARCHAR(1000)', 0, 'Jobsub submit options'),
                           ('jobsub_start', 'jobsub_start', 'VARCHAR(1000)', 0, 'Jobsub start job submit options'),
                           ('jobsub_timeout', 'jobsub_timeout', 'INT', 0, 'Jobsub timeout'),
                           ('schema_', 'schema', 'VARCHAR(1000)', 0, 'Sam schema'),
                           ('validate_on_worker', 'check', 'INT', 0, 'Validate on worker flag'),
                           ('copy_to_fts', 'copy', 'INT', 0, 'Copy to FTS flag'),
                           ('script', 'script', 'VARCHAR(1000)', 0, 'Batch script'),
                           ('start_script', 'startscript', 'VARCHAR(1000)', 0, 'Batch start script'),
                           ('stop_script', 'stopscript', 'VARCHAR(1000)', 0, 'Batch stop script'),
                           ('data_streams', 'datastream', 'INT', 1, 'Data streams'),
                           ('ana_data_streams', 'anadatastream', 'INT', 1, 'Analysis data streams'),
                           ('init_scripts', 'initscript', 'INT', 1, 'Initialization scripts'),
                           ('init_sources', 'initsource', 'INT', 1, 'Initialization soruces'),
                           ('end_scripts', 'endscript', 'INT', 1, 'End scripts'),
                           ('', '', 'FOREIGN KEY (project_id) REFERENCES projects (id)', 0, '')],
                'substages': [('id', '', 'INT NOT NULL PRIMARY KEY AUTO_INCREMENT', 0, 'Substage ID'),
                              ('fclname', '', 'VARCHAR(1000) NOT NULL', 0, 'Fcl file'),
                              ('stage_id', '',  'INT NOT NULL', 0, 'Parent stage ID'),
                              ('seqnum', '', 'INT', 0, 'Sequence number'),
                              ('init_sources', 'initsource', 'INT', 1, 'Initialization sources'),
                              ('end_scripts', 'endscript', 'INT', 1, 'End scripts'),
                              ('projectname', 'projectname', 'VARCHAR(1000)', 0, 'Project name override'),
                              ('stagename', 'stagename', 'VARCHAR(1000)', 0, 'Stage name override'),
                              ('version', 'version', 'VARCHAR(1000)', 0, 'Sam version override'),
                              ('output', 'output', 'VARCHAR(1000)', 0, 'Output name override'),
                              ('exe', 'exe', 'VARCHAR(1000)', 0, 'Executable'),
                              ('', '', 'FOREIGN KEY (stage_id) REFERENCES stages (id)', 0, '')],
                'strings': [('id', '', 'INT NOT NULL PRIMARY KEY AUTO_INCREMENT', 0, 'String ID'),
                            ('array_id', '', 'INT NOT NULL', 0, 'Array ID'),
                            ('value', '', 'VARCHAR(1000) NOT NULL', 0, 'String value')]}

