import re
import pywikibot
from pywikibot import pagegenerators

CASE_SECTION_RE = re.compile(r'^\s*==\s*([^=]*)\s*==\s*$', re.MULTILINE)
TASK_LINE_RE = re.compile('{{ArbComOpenTasks\/line.*\|name=(.*)\|.*}}', re.DOTALL)

def main(*args) -> None:
    local_args = pywikibot.handle_args(args)

    #case_page_name = 'Wikipedia:Arbitration/Requests/Case'
    #task_page_name = 'Template:ArbComOpenTasks/CaseRequests'
    case_page_name = 'User:GeneralBotability/invalid'
    task_page_name = 'User:GeneralBotability/invalid'

    # Loading the arguments
    for arg in local_args:
        option, _, value = arg.partition(':')
        if option == '-case-page':
            case_page_name = value
        if option == '-task-page':
            task_page_name = value

    site = pywikibot.Site()
    case_page = pywikibot.Page(pywikibot.Link(case_page_name, site))
    task_page = pywikibot.Page(pywikibot.Link(task_page_name, site))
    # Iterate over the case page and pull all cases (level-2 headers)
    case_page_case_set = set([c.strip() for c in CASE_SECTION_RE.findall(case_page.get())])
    task_page_case_set = set([t.strip() for t in TASK_LINE_RE.findall(task_page.get())])

    add_to_tasks = case_page_case_set - task_page_case_set
    remove_from_tasks = task_page_case_set - case_page_case_set
    print(add_to_tasks)
    print(remove_from_tasks)
    for case_name in add_to_tasks:
        task_page_contents = task_page.text
        task_page_contents += '\n{{ArbComOpenTasks/line' + \
                              '\n|mode=caserequest' + \
                              '\n|name={}'.format(case_name) + \
                              '\n|date={{subst:CURRENTDAY}} {{subst:CURRENTMONTHABBREV}} {{subst:CURRENTYEAR}}' + \
                              '\n}}'
        task_page.text = task_page_contents
        print(task_page.text)
        task_page.save(summary='Clerkbot: maintain CaseRequests, adding new case {}'.format(case_name))
    for case_name in remove_from_tasks:
        task_page_contents = task_page.text
        # Why twice as many curly braces? They tell the python format string that
        # these are literal braces, not replacement targets
        case_re = r'\n{{{{ArbComOpenTasks\/line\s*\|mode=caserequest\s*\|name={}\s*\|date=.*\s*}}}}'.format(case_name)
        task_page.text = re.sub(case_re, '', task_page.text)
        print(task_page.text)
        task_page.save(summary='Clerkbot: maintain CaseRequests, removing {} (no longer at [[{}]])'.format(case_name, case_page))
    

if __name__ == '__main__':
    main()
