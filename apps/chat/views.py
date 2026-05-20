from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from .models import Conversation, Message
from apps.accounts.models import CustomUser

@login_required(login_url='accounts:login')
def start_conversation(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    if other_user == request.user:
        return redirect('accounts:dashboard')

    # Find if conversation already exists between these two specifically (1v1)
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=other_user)
    
    # We want to ensure it's a 1v1 conversation
    conversation = None
    for conv in conversations:
        if conv.participants.count() == 2:
            conversation = conv
            break
            
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('chat:conversation_detail', conversation_id=conversation.id)

@login_required(login_url='accounts:login')
def chat_index(request):
    # Fetch all conversations for the user
    conversations = request.user.conversations.annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time', '-created_at')
    
    conversations_data = []
    for convo in conversations:
        other_user = convo.get_other_user(request.user)
        last_message = convo.get_last_message()
        conversations_data.append({
            'conversation': convo,
            'other_user': other_user,
            'last_message': last_message
        })
    
    context = {
        'conversations_data': conversations_data,
        'active_conversation': None
    }
    return render(request, 'chat/chat.html', context)

@login_required(login_url='accounts:login')
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.messages.exclude(sender=request.user).update(is_seen=True)
            return redirect('chat:conversation_detail', conversation_id=conversation.id)

    # Also mark as seen when just viewing
    conversation.messages.exclude(sender=request.user).update(is_seen=True)

    conversations = request.user.conversations.annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time', '-created_at')
    
    conversations_data = []
    for convo in conversations:
        other_user = convo.get_other_user(request.user)
        last_message = convo.get_last_message()
        conversations_data.append({
            'conversation': convo,
            'other_user': other_user,
            'last_message': last_message
        })
    
    messages = conversation.messages.order_by('timestamp')
    
    context = {
        'conversations_data': conversations_data,
        'active_conversation': conversation,
        'messages': messages,
        'other_user': conversation.get_other_user(request.user)
    }
    return render(request, 'chat/chat.html', context)
