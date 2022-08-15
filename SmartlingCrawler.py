import regex as re
from urllib.request import urlopen
import base64
import requests
from bs4 import BeautifulSoup
from  respond_handler import Respond_Handler
from Data import *
LOCKED = '你的账户已被Smartling禁封'

TIME_OUT_MESSAGE = '官网服务器没有回应:'

USER_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
               "Upgrade-Insecure-Requests": "1",
               "DNT": "1",
               "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               "Accept-Language": "en-US,en;q=0.9",
               "Accept-Encoding": "gzip, deflate",
               'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',}

TIMEOUT = 6
LOGIN_URL = 'https://dashboard.smartling.com/sso/login.htm'
AUTHENTICATE = 'https://sso.smartling.com/auth/realms/Smartling/login-actions/authenticate'
REQUEST_URL = 'https://dashboard.smartling.com/p/graphql-api/v1'
CREATE_TASK_URL_L = 'https://dashboard.smartling.com/p/content-assignments-api/v2/projects/'
CREATE_TASK_URL_R = '/claiming/tasks/create'

class SmartlingCrawler():
    def __init__(self,ui):
        self.ui = ui
        self.session = None
        self.headers = USER_HEADER
        self.username = None
        self.password = None
        self.respond = None
        self.userID = None
        self.authenticate_code = None
        self.execution = None
        self.respond_handler = Respond_Handler()
        self.current_sku = None

    # def enter_password_ID(self,username,password):
    #     self.username = username
    #     self.password = password

    def clear(self):
        self.session.close()
        self.session.headers = USER_HEADER
        self.respond = None
        self.userID = None
        self.authenticate_code = None
        self.execution = None
        self.current_sku = None

    def add_one_sku(self,sku_string):
        self.current_sku = sku_string
        search_result = self.search(sku_string)
        if isinstance(search_result, Task):
            new_task = search_result
        else:
            return False
        new_task = self.create_task(new_task)
        assign_result = self.assign_task(new_task)
        if assign_result is True:
            return True
        else:
            return -1

    def login(self,username , password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        # print(self.username)
        # print(self.password)
        payload = {
            'username':  self.username,
            'password':  self.password
        }
        try:
            login_respond = self.session.get(LOGIN_URL, timeout=TIMEOUT ,headers=USER_HEADER )
            login_respond_text = BeautifulSoup(login_respond.text, 'html.parser')
            authurl = str(login_respond_text.find("form", {"id": "kc-form-login"})['action'])
            # print(authurl)
            self.authenticate_code= re.search(r'(?<=(authenticate.*code=)).*(?=&execution=)',authurl).group(0)
            self.execution= re.search(r'(?<=(&execution=)).*$', authurl).group(0)
            params = {
                'code': self.authenticate_code,
                'execution': self.execution,
            }

            auth_respond = self.session.post(authurl,params=params, data=payload,headers=USER_HEADER)
            auth_respond_text = BeautifulSoup(auth_respond.text, 'html.parser')
            # print(auth_respond_text)
            try:
                self.userID = (auth_respond_text.find("div", {"class": "app-body"})['data-user-uid'])
                return True
            except TypeError:
                self.clear()
                return False

            # print(self.userID)
        except requests.exceptions.Timeout:
            print(TIME_OUT_MESSAGE+LOGIN_URL)

    def get_url(self,url):
        try:
            self.respond = self.session.get(url, timeout=TIMEOUT, headers=USER_HEADER )
        except requests.exceptions.Timeout:
            print(TIME_OUT_MESSAGE+url)

    def search(self,sku_id):
        new_task = Task(sku_id)
        json_data ={
            'operationName': 'JobsList',
            'variables': {
                'options': {
                    'filter': {
                        'query': sku_id,
                    },
                    'preset': 'AVAILABLE_TO_ACCEPT',
                    'grouping': {
                        'timezone': 'America/Toronto',
                    },
                    'paging': {
                        'offset': 0,
                        'limit': 500,
                    },
                },
                'withCustomFields': False,
                'withProjectLabels': False,
            },
            'query': 'query JobsList($options: JobsListQueryInput!, $withCustomFields: Boolean!, $withProjectLabels: Boolean!) {\n  jobsList(options: $options) {\n    jobs {\n      ...JobGroupItemFragment\n      __typename\n    }\n    jobsCountByPreset {\n      ...JobsByPresetCountFragment\n      __typename\n    }\n    workNotInJob {\n      ...WorkNotInJobFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment JobGroupItemFragment on Job {\n  completedDate\n  createdBy {\n    firstName\n    lastName\n    userUid\n    __typename\n  }\n  createdDate\n  dueDate\n  id\n  issues {\n    sourceIssuesCount\n    translationIssuesCount\n    __typename\n  }\n  jobActions {\n    actionType\n    id\n    primaryAction\n    __typename\n  }\n  jobName\n  description\n  jobNumber\n  jobStatus\n  priority\n  progress {\n    percentComplete\n    totalWordCount\n    __typename\n  }\n  accountName\n  accountUid\n  sourceLocaleId\n  sourceLocaleDescription\n  agencyUid\n  projectId\n  projectName\n  projectType\n  projectLabels @include(if: $withProjectLabels) {\n    id\n    labelName\n    __typename\n  }\n  qcs {\n    lastUpdated\n    value\n    __typename\n  }\n  referenceNumber\n  riskFactor {\n    value\n    __typename\n  }\n  summaryReport {\n    ...JobItemSummaryReportFragment\n    __typename\n  }\n  targetLocaleIds\n  translationJobUid\n  aggregatedPerLocale {\n    localeId\n    localeDescription\n    inProgressWordCount\n    toAssignWordCount\n    totalWordCount\n    translatedWordCount\n    issuesCount\n    __typename\n  }\n  aggregatedPerWorkflowStep {\n    stepData {\n      key\n      percentSaved\n      name\n      type\n      value\n      __typename\n    }\n    __typename\n  }\n  aggregatedPerWorkflow {\n    ...AggregatedWorkflow\n    __typename\n  }\n  authorizedBy {\n    firstName\n    lastName\n    userUid\n    authorizedDate\n    __typename\n  }\n  translatorTasks {\n    ...JobTranslatorTaskFragment\n    __typename\n  }\n  submittedTasks {\n    ...JobSubmittedTaskFragment\n    __typename\n  }\n  customFields @include(if: $withCustomFields) {\n    fieldType\n    fieldName\n    fieldUid\n    fieldValue\n    __typename\n  }\n  __typename\n}\n\nfragment JobItemSummaryReportFragment on JobSummaryReportItem {\n  stringCount\n  wordCount\n  workflowStepType\n  __typename\n}\n\nfragment AggregatedWorkflow on AggregatedPerWorkflow {\n  workflowUid\n  workflowName\n  targetLocales {\n    localeId\n    targetLocaleDescription\n    workflowSteps {\n      toAssignWordCount\n      translatedWordCount\n      totalWordCount\n      workflowStepType\n      workflowStepName\n      workflowStepOrder\n      workflowStepUid\n      workflowStepClass\n      contentAssignmentEnabled\n      workflowStepDueDate\n      contentAssignments {\n        firstName\n        lastName\n        email\n        wordCount\n        userUid\n        __typename\n      }\n      __typename\n    }\n    stepData {\n      key\n      value\n      type\n      name\n      percentSaved\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment JobTranslatorTaskFragment on JobTranslatorTask {\n  claiming {\n    isClaimable\n    isUnclaimable\n    claimableWordCount\n    __typename\n  }\n  dueDate\n  gracefulWindow\n  isActionable\n  isContentUpdated\n  isDeclined\n  issues {\n    issuesCount\n    __typename\n  }\n  offlineWorkEnabled\n  originalLocaleId\n  precedingWorkflowStep {\n    precedingWorkflowStepUid\n    __typename\n  }\n  stringCount\n  targetLocaleId\n  targetLocaleDescription\n  wordCount\n  translatedWordCount\n  workflowStep {\n    workflowStepName\n    workflowStepType\n    workflowStepUid\n    __typename\n  }\n  upcomingTask {\n    precedingWorkflowStep {\n      precedingWorkflowStepUid\n      __typename\n    }\n    wordCount\n    stringCount\n    workflowStep {\n      workflowStepUid\n      workflowStepName\n      workflowStepType\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment JobSubmittedTaskFragment on JobSubmittedTask {\n  targetLocaleId\n  targetLocaleDescription\n  wordCount\n  weightedWordCount\n  __typename\n}\n\nfragment JobsByPresetCountFragment on JobsByPresetCount {\n  ALL\n  ACTIVE\n  LATE\n  DUE_SOON\n  AT_RISK\n  CREATED_BY_ME\n  RECENTLY_CREATED\n  HIGH_PRIORITY\n  OPEN_ISSUES\n  REQUIRE_ASSIGNMENT\n  AVAILABLE_TO_APPROVE\n  AVAILABLE_TO_ACCEPT\n  CURRENT_WORK\n  COMPLETED\n  UPCOMING\n  SUBMITTED\n  DECLINED\n  __typename\n}\n\nfragment WorkNotInJobFragment on ContentNotInJob {\n  id\n  projectId\n  projectName\n  accountUid\n  accountName\n  issues {\n    sourceIssuesCount\n    translationIssuesCount\n    __typename\n  }\n  translatorTasks {\n    targetLocaleId\n    targetLocaleDescription\n    originalLocaleId\n    workflowStep {\n      workflowStepName\n      workflowStepUid\n      workflowStepType\n      __typename\n    }\n    wordCount\n    stringCount\n    __typename\n  }\n  __typename\n}\n',
        }
        self.session.headers.update({'content-type': 'application/json'})
        self.respond = self.session.post(REQUEST_URL, json=json_data)
        check = self.respond_handler.check_search_respond(self.respond)

        if check is True:
            new_task.create(self.respond)
            return new_task
        else:
            return False


    def create_task(self, new_task):
        projectID = new_task.projectUid
        workflowStepUid = new_task.workflowStepUid
        translationJobUid = new_task.translationJobUid
        json_data = {
            'localeId': 'zh-CN',
            'workflowStepUid': workflowStepUid,
            'translationJobUid': translationJobUid,
            'targetTaskWords': 2000,
        }
        self.session.headers.update({'content-type': 'application/json'})
        create_task_url = CREATE_TASK_URL_L+projectID+CREATE_TASK_URL_R
        self.respond = self.session.post(create_task_url, json=json_data)
        new_task.assignTask(self.respond)
        # print(self.respond.text)
        return new_task

    def assign_task(self,new_task):
        projectID = new_task.projectUid
        workflowStepUid = new_task.workflowStepUid
        translationJobUid = new_task.translationJobUid
        assignmentTaskUids = new_task.assignmentTaskUids

        json_data = {
            'operationName': 'AcceptTask',
            'variables': {
                'userUid': self.userID,
                'projectUid': projectID,
                'jobUid': translationJobUid,
                'workflowStepUid': workflowStepUid,
                'localeId': 'zh-CN',
                'assignmentTaskUids': assignmentTaskUids,
            },
            'query': 'mutation AcceptTask($userUid: String!, $projectUid: String!, $jobUid: String!, $workflowStepUid: String!, $localeId: String!, $assignmentTaskUids: [String!]!) {\n  acceptTasks(\n    userUid: $userUid\n    projectUid: $projectUid\n    jobUid: $jobUid\n    workflowStepUid: $workflowStepUid\n    targetLocaleId: $localeId\n    assignmentTaskUids: $assignmentTaskUids\n  )\n}\n',
        }

        self.session.headers.update({'content-type': 'application/json'})

        self.respond = self.session.post(REQUEST_URL, json=json_data)
        respond_result = self.respond_handler.check_assign_respond(self.respond)
        return respond_result


