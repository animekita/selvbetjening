from django.db import models
from django.contrib.auth.models import User, Group

from sorl.thumbnail.fields import ThumbnailField

class GroupRemoteRole(models.Model):

    database_id = models.CharField(max_length=100)
    group = models.ForeignKey(Group)
    remote_role_id = models.IntegerField()

    class Meta:
        app_label = 'vanillaforum'
        unique_together = (('group', 'remote_role_id', 'database_id'),)

class Settings(models.Model):

    user = models.ForeignKey(User)

    # Notify me when people comment on my discussions
    notify_comment_discussions_popup = models.BooleanField(default=True)
    notify_comment_discussions_email = models.BooleanField(default=False)

    # Notify me when people mention me in discussion titles
    notify_mentioned_in_titles_popup = models.BooleanField(default=True)
    notify_mentioned_in_titles_email = models.BooleanField(default=False)

    # Notify me when people mention me in comments
    notify_mentioned_in_comments_popup = models.BooleanField(default=True)
    notify_mentioned_in_comments_email = models.BooleanField(default=False)

    # Notify me when people comment on my bookmarked discussions
    notify_comment_bookmarked_popup = models.BooleanField(default=True)
    notify_comment_bookmarked_email = models.BooleanField(default=False)

    # Notify me when people start new discussions
    notify_new_discussion_email = models.BooleanField(default=False)

    # Notify me of private messages
    notify_private_message_popup = models.BooleanField(default=True)
    notify_private_message_email = models.BooleanField(default=False)

    # Notify me when I am added to private conversations
    notify_private_message_added_popup = models.BooleanField(default=True)
    notify_private_message_added_email = models.BooleanField(default=False)

    # Profile picture
    picture = ThumbnailField(upload_to='pictures/vanilla-forum/', blank=True, default='', size=(100,100), quality=100)

    class Meta:
        app_label = 'vanillaforum'

    def update_preferences(self, preferences):
        options = (('Popup.DiscussionComment', self.notify_comment_discussions_popup),
                   ('Email.DiscussionComment', self.notify_comment_discussions_email),
                   ('Popup.DiscussionMention', self.notify_mentioned_in_titles_popup),
                   ('Email.DiscussionMention', self.notify_mentioned_in_titles_email),
                   ('Popup.CommentMention', self.notify_mentioned_in_comments_popup),
                   ('Email.CommentMention', self.notify_mentioned_in_comments_email),
                   ('Popup.BookmarkComment', self.notify_comment_bookmarked_popup),
                   ('Email.BookmarkComment', self.notify_comment_bookmarked_email),
                   ('Email.NewDiscussion', self.notify_new_discussion_email),
                   ('Popup.ConversationMessage', self.notify_private_message_popup),
                   ('Email.ConversationMessage', self.notify_private_message_email),
                   ('Popup.AddedToConversation', self.notify_private_message_added_popup),
                   ('Email.AddedToConversation', self.notify_private_message_added_email))

        for key, selected in options:
            if selected:
                preferences[key] = '1'
            else:
                preferences.pop(key, None)

        return preferences
