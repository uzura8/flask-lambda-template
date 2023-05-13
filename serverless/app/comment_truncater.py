from app.common.log import output_log
from app.models.dynamodb import Comment, CommentCount


def handler(event=None, context=None):
    try:
        output_log('START: comment_truncater.handler')
        output_log(['comment_truncater.handler:event', event])

        Comment.truncate()
        CommentCount.truncate()

        output_log('END: comment_truncater.handler')
        return 'Success'

    except Exception as e:
        output_log(e, 'error')
        return 'END: comment_truncater.handler: Error'
