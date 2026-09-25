from django import template

register = template.Library()

@register.filter
def get_cards_for_column(lists, col_name):
    name_lower = col_name.lower()
    
    # Define mapping keywords for the 5 default columns
    mappings = {
        "backlog": ["backlog", "idea"],
        "to do": ["to do", "todo", "prompt", "ready"],
        "in progress": ["progress", "doing", "active", "generation"],
        "review/testing": ["review", "test", "edit", "verify"],
        "done": ["done", "complete", "publish", "finish"]
    }
    
    keywords = mappings.get(name_lower, [name_lower])
    
    cards = []
    for kanban_list in lists:
        list_name_lower = kanban_list.name.lower()
        if any(kw in list_name_lower for kw in keywords):
            cards.extend(list(kanban_list.cards.all()))
            
    return cards
