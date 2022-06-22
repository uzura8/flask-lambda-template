from app.common.log import output_log


class CommentImporter:


    def __init__(self):
        pass


    def __del__(self):
        pass


    def execute(self):
        pass


def handler(event=None, context=None):
    try:
        output_log('START: comment_importer.handler')
        output_log(['comment_importer.handler:event', event])

        ci = CommentImporter()
        ci.execute()

        output_log('END: comment_importer.handler: Success')
        return 'Success'

    except Exception as e:
        output_log(e, 'error')
        return 'END: comment_importer.handler: Error'
