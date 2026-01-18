#!/usr/bin/env python3

import os
import sys
sys.path.append('/home/bhaskar/cd/campusguide')

from openai import OpenAI
from config.config import Config

def main():
    config = Config()
    
    client = OpenAI(
        api_key=config.API_KEY,
        base_url=config.API_BASE_URL
    )
    
    # The full text from the PDF
    context = """The ICFAI Foundation for Higher Education
Faculty of Science & Technology
Training and placement Office (TPO)
Rules and Regulations
For AY: 2025-26
A. ELIGIBILITY & REGISTRATION:
1. TPO aims to provide placement assistance for all final year
 students. Placement is a privilege extended                  to the students but can't be claimed as a matter of right.
2. Students should register their names by submitting the Stud
ents' Data Sheet as per the prescribed                        format given by the TPO. Only those students who have register
ed are eligible to participate in the                         placement activities.
3. Campus placement is a facility provided to the students. Re
gistration is compulsory for the interested                   students and not interested in placement are advised not to re
gister.                                                       4. Students will be allowed to have a single job offer only, p
rovided:                                                      a.
Category -I : - Up to 6 LPA (Safe Offer)
Category -II : - ≥ 6.0 LPA & ≤ 10 LPA (Safe offer; Category-I 
students cannot apply)                                        Category -III : - > 10 LPA to ≤ 14.0 LPA (Dream offer for only
 Category –I students;                                        Category-II students cannot apply)
Category -IV : - 14.0 LPA and above (Dream offer for all categ
ories; Students of all                                        categories; I, II & III can apply)
b. Once a student bags a job offer from a dream company, he/ s
he will not be allowed to                                     participate in any campus recruitment process at all. Moreover
, already placed students but                                 not placed in "Dream Company" shall be allowed for the second 
job offers after completion                                   of 80% placement of registered and eligible students of indivi
dual discipline.                                              c. The above policy categorization will be strictly followed. 
Therefore, it’s the responsibility of                         each student to decide carefully before attending the process 
of a company.                                                 5. The eligibility criteria imposed by the visiting company wi
ll be the final.                                              6. Invariably each company keeps a clause of service agreement
 (2 to 3 years), the students post joining                    should abide by that. Service agreement imposed by a company s
hould not be a hindrance for a student                        to opt for a company’s process
7. TPO arranges company from pan India location and as such co
mpany location should not be a                                constraint for a student while opting for a company
8. The eligible/registered students must attend all the traini
ng programs/workshops arranged by the TPO.                    For the students who are not participating in any of the activ
ities will be participating in placements                     process on their own risk and TPO doesn’t hold any responsibil
ity for the same.                                             9. All kinds of clarifications & communications (such as regis
tration for placement assistance, updating                    the database, etc.,) should be executed through TPO only.
10. If any student is not applying consistently for 3 applicab
le companies, he /she will be debarred from                   the entire process of placement for the whole academic year.
11. During induction, most of the companies insist on Passport
 and PAN card. Thus, the students are                         expected to apply for the same at the earliest.
12. Students may have to manage their own transport arrangemen
ts to return home and inform their                            parents well in advance if the proceedings on the date of the 
selection process continue till the late                      evening.
13. Based on the directions given by the companies, students m
ay be sent to attend pooled campus                            placement drives in other colleges. Students should inform the
ir parents about the placement process,                       venue, and timings in advance.
14. Students attending campus interviews should adhere to the 
following instructions,                                       a) Report at the venue of pre-placement talk and interview as 
per the instructions.                                         b) Students should carry a minimum of 3 copies of their resume
, photocopies of all Original                                 certificates, and 5 passport size photographs.
c) A student in casual dress will not be allowed for the PPT/R
ecruitment Process.                                           B. RESUME
15. Students are expected to follow the institute resume templ
ate (already shared) for preparing the                        resumes.
16. The details given in the resume have to be genuine and any
 student found violating this will be                         disallowed from the placement for the rest of the academic yea
r.                                                            C. PRE-PLACEMENT TALKS (PPT)
17. Students should be seated in the venue 15 minutes before t
he scheduled start of the PPT.                                18. All Students must attend in all the companies visiting for
 pre-placement talk.                                          19. Any clarification regarding salary break-up, job profile, 
place of work, bond details, date of joining,                 etc. must be sought from the companies during PPT or interview
.                                                             20. DRESS CODE: Students must be formally dressed whenever the
y participate in any interaction with a                       company
**This office reserves the right to refuse permission to a stu
dent to attend the selection                                  process/PPT if they do not dress up formally. Students are exp
ected to know the norms for                                   formal wear; for the benefit of those who claim ignorance, ple
ase note that the following are                               strictly not allowed:
• T-shirts with printed text; un-collared T-shirts;
• Shorts
• Jeans
• Shirt not-tucked in
• Chappals / flip-flops
D. PLACEMENT PROCESS
21. It is the responsibility of the student to check announcem
ents/notices / updated information /                          shortlisted names etc. in the notice boards of the TPO Notice 
Board.                                                        22. During the process if any student has any issues should im
mediately brought to the notice of the TPO                    or corresponding Placement Manager.
23. ATTENDANCE & PUNCTUALITY:
a. A student who applies and gets shortlisted is bound to go t
hrough the entire selection process unless                    rejected midway by the company. Any student who withdraws deli
berately in the middle of a selection                         process will be disallowed from placement for the rest of the 
academic year.                                                b. LATE COMERS FOR APTITUDE TEST / GD / INTERVIEW will not be 
allowed to appear for the                                     selection process.
24. DISCIPLINE:
a) Students should maintain discipline and exhibit etiquette i
n every action they take during the                           placement process. Any student found violating the discipline 
rules set by the company or defaming                          the institute's name will be disallowed from the placements fo
r the rest of the academic year.                              b) Students found cheating or misbehaving in the selection pro
cess (Test / GD / Interview) will be                          disallowed from the placements for the rest of the academic ye
ar.                                                           E. JOB OFFERS
25. A copy of the offer letter is required to be submitted by 
the student select to the placement office.                   26. If a student is offered a second job, he/she must give a l
etter of regret to the company, which offered                 the first job and a letter of acceptance to the second.
27. After accepting a job offer, if any student decides to wit
hdraw his/her acceptance any time during the                  year, he/she must inform the company concerned through the TPO
 immediately. Student rejecting a                             particular offer shall not be allowed to apply for further com
panies, under any circumstances.                              28. Post Placement: Due to unknown reasons, if the Company del
ay or stop boarding student selects, in                       that case the institute does not stand responsible for the sam
e                                                             Rejection grounds for students:
29. Students may be debarred /blacklisted from the placement i
f he/she is found involved in any act of                      indiscipline or engaged in malpractices during their academics
30. Students giving wrong data/information to the Training and
 Placement Coordinators, He/she will be                       debarred from the placement activities for the rest of the aca
demic year.                                                   31. Students cannot drop out from the selection process once h
e/she has been shortlisted for further rounds                 after the first round selection. Disciplinary action will be t
aken against defaulter student/s.                             32. Any kind of misbehavior/complaints reported by the company
 officials/ faculty/ staff/ volunteers will                   be taken seriously & those evolve will be debarred/ blackliste
d from future campus placements                               33. For all matters not covered by the above regulations, the 
Placement Office will use its discretion to                   take appropriate decisions. The decision taken by this office 
shall be binding on all students/scholars.                    Placement team Endorsed by: - ICFAI-Tech
The Director - IcfaiTech, IFHE
DECLARATION BY THE STUDENT / PARENT / GAURDIAN:
I hereby certify that I have read the entire terms and conditi
ons as mentioned above of the Training &                      Placement Department. I shall abide by the terms & conditions 
as well as all clauses contained therein.                     Name of the Student: Name of the Parent:
Enrolment No: Mobile No:
Mobile No: Email-ID:
Registered Email: Occupation:
Branch : Address: Aurangabad Maharashtra
Signature of the Student Signature of the Parent
Date: Date:"""
    
    query = "What documents are students expected to have during placement induction?"
    
    prompt = f"""You are CampusGuide, an AI assistant for ICFAI University students, faculty, and staff.

Your task is to answer questions using ONLY the provided document context. You must NEVER use external knowledge, assumptions, or information not present in the given documents.

INSTRUCTIONS:
1. Synthesize information from ALL provided context to create a complete answer
2. Combine related policy rules from different parts into a coherent explanation
3. Present the answer in clear, student-friendly bullet points
4. Only refuse with "The requested information is not available in the provided documents." if NO relevant information exists
5. For policy questions, summarize and organize the rules, restrictions, and procedures mentioned
6. Cite the document name and relevant sections

CONTEXT:
{context}

QUESTION: {query}

Provide a comprehensive answer based on the context above. Format your response as bullet points explaining the policy rules and procedures."""
    
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        answer = response.choices[0].message.content
        print("Answer from Groq:")
        print(answer)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()