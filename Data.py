import regex as re
import requests
from bs4 import BeautifulSoup


class Task():
    def __init__(self, skuID):
        self.skuID = skuID
        self.projectUid = None
        self.translationJobUid =None
        self.assignmentTaskUids = []
        self.workflowStepUid: None
        self.is_populated = False


    def create(self,respond):
        respond_text = respond.text
        # print(respond_text)
        self.projectUid = re.search(r'(?<=(\"projectId\"\:\"))[a-z0-9]+(?=\")', respond_text).group(0)
        # print(self.projectUid)
        self.translationJobUid = re.search(r'(?<=(\"translationJobUid\"\:\"))[a-z0-9]+(?=\")', respond_text).group(0)
        # print(self.translationJobUid )
        self.workflowStepUid = re.search(r'(?<=(\"workflowStepUid\"\:\"))[a-z0-9]+(?=\")', respond_text).group(0)
        # print(self.workflowStepUid )
        self.is_populated = True

    def assignTask(self,respond):
        respond_text = respond.text
        task_queue = re.findall(r'\"taskUid\"\:\"([a-z0-9]+)\"', respond_text)
        # print(task_queue)
        for each_task in task_queue:
            self.assignmentTaskUids.append(each_task)

