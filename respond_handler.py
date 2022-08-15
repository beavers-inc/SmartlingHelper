class Respond_Handler():
    def __init__(self):
        pass

    def check_search_respond(self,respond):
        respond_text = respond.text
        # check if more than 1 search result
        number_of_skus = respond_text.count('"id":')
        # print(number_of_skus)
        if number_of_skus== 1:
            return True
        else:
            return False

    def check_assign_respond(self,respond):
        respond_text = respond.text
        success_key = '{"acceptTasks":true}'
        if success_key in respond_text:
            return True
        else:
            return False
