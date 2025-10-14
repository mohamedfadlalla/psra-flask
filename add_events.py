from app import app, db
from models import Event
from datetime import datetime

def add_events():
    with app.app_context():
        events_data = [
            {
                'title': 'Research Introduction and Research Design',
                'description': 'A lecture covering the basics of research, the research process, types of research designs, and ethics in scientific writing.',
                'presenter': 'Dr. Mohamed Fadlalla',
                'date': '2025-06-14',
                'time': '20:00',
                'url': 'https://t.me/psrafpsa/27',
                'image': '1.png'
            },
            {
                'title': 'How to Write a Research Proposal',
                'description': 'An insightful session covering key aspects of scientific research and proposal writing, including structure, ethics, and method steps.',
                'presenter': 'Dr. Safaa Abdelraheem',
                'date': '2025-06-17',
                'time': '21:00',
                'url': 'https://t.me/psrafpsa/37',
                'image': '2.png'
            },
            {
                'title': 'Find a Needle in a Haystack: Sources of Information in Pharmaceutical Science',
                'description': 'A session on the meaning and importance of literature in pharmacy, sources of information, and how to search scientific literature.',
                'presenter': 'Dr. Ghaida Mustafa',
                'date': '2025-06-20',
                'time': '21:00',
                'url': 'https://t.me/psrafpsa/60',
                'image': '3.png'
            },
            {
                'title': 'Types of Study Design',
                'description': 'This lecture bridges the gap between conceptual hypothesis and practical application, covering the scientific method and study design classifications.',
                'presenter': 'Dr. Mawahib Ahmed',
                'date': '2025-06-23',
                'time': None,
                'url': 'https://t.me/psrafpsa/72',
                'image': '4.png'
            },
            {
                'title': 'Sampling Techniques and Data Collection Methods',
                'description': 'A session covering why and how to sample, different sampling methods, and data collection tools like questionnaires and interviews.',
                'presenter': 'Dr. Walaa Wagiealla',
                'date': '2025-06-26',
                'time': '21:00',
                'url': 'https://t.me/psrafpsa/90',
                'image': '5.png'
            },
            {
                'title': 'Scientific Writing, Plagiarism and Reference Management',
                'description': 'This lecture covers types of scientific articles, writing style, reference tools, and how to avoid plagiarism.',
                'presenter': 'Dr. Fakhereddin Babiker',
                'date': '2025-07-02',
                'time': '21:00',
                'url': 'https://t.me/psrafpsa/109',
                'image': '6.png'
            },
            {
                'title': 'A Journey from Research to Publication',
                'description': 'A session detailing the entire process from conducting research to getting the findings published.',
                'presenter': 'Dr. Ahmed H Arbab',
                'date': '2025-07-05',
                'time': '21:00',
                'url': 'https://t.me/psrafpsa/116',
                'image': '7.png'
            },
            {
                'title': 'Systemic Review & Meta-Analysis: An Overview',
                'description': 'Explore how researchers use Systematic Reviews and Meta-Analyses to draw reliable conclusions, covering essential steps and tools.',
                'presenter': 'Dr. Gareth Dyke',
                'date': '2025-07-08',
                'time': '20:00',
                'url': 'https://t.me/psrafpsa/127',
                'image': '8.png'
            },
            {
                'title': 'Rational and Ethical Use of AI in Research',
                'description': 'An online workshop guiding students on the responsible use of AI in science, from literature review and data analysis to practical applications.',
                'presenter': 'Dr. Mohammed Osman Mahjoub',
                'date': '2025-09-10',
                'time': '20:00',
                'url': 'https://t.me/psrafpsa',
                'image': '9.png'
            },
            {
                'title': 'AI\'s Transformative Impact on Medicine: From Drug Discovery to Personalized Care',
                'description': 'A workshop exploring how AI is revolutionizing healthcare by accelerating drug discovery, optimizing clinical trials, and enabling personalized medicine.',
                'presenter': 'Dr. Mohamed Fadlalla',
                'date': '2025-09-13',
                'time': '20:00',
                'url': 'https://t.me/psrafpsa',
                'image': '10.png'
            },
            {
                'title': 'ResearchInAction - Research Implementation Session',
                'description': 'A special session on how to work effectively in a research team, when to seek supervisor support, and how to translate findings into real-world impact.',
                'presenter': 'Dr. Ahmed Hassan Arbab',
                'date': '2025-08-06',
                'time': '11:30',
                'url': 'https://t.me/psrafpsa',
                'image': '11.png'
            },
            {
                'title': 'Types of Scientific Research in Pharmacy Field (Video)',
                'description': 'A video exploring the different types of scientific research in pharmacy and their role in driving discoveries and innovation.',
                'presenter': None,
                'date': '2025-01-01',  # Past date for archived
                'time': None,
                'url': 'https://www.facebook.com/share/v/178xxqMD3b/?mibextid=wwXIfr',
                'image': '12.png'
            },
            {
                'title': 'Sudanese Research Journey That Inspires: From Khartoum To London (Video)',
                'description': 'An inspiring story of University of Khartoum students who transformed a classroom idea into a remarkable academic journey to University College London.',
                'presenter': None,
                'date': '2025-01-01',  # Past date for archived
                'time': None,
                'url': 'https://www.facebook.com/share/v/1BBnTVoCvx/?mibextid=wwXIfr',
                'image': '13.png'
            },
            {
                'title': 'Research Journeys: Inspiring Stories (with Ahmed Bushra)',
                'description': 'Discover the role of scientific research in pharmacy and the personal journey of Ahmed Bushra, including challenges he encountered.',
                'presenter': 'Ahmed Bushra',
                'date': '2025-01-01',  # Past date for archived
                'time': None,
                'url': 'https://www.facebook.com/fpsauofk/videos/704363348883857/?app=fbl',
                'image': '14.png'
            },
            {
                'title': 'Research Journeys: Inspiring Stories (with Mazen Bushra)',
                'description': 'Explore the significance of scientific research and its benefits for graduated students through the personal journey of Mazen Bushra.',
                'presenter': 'Mazen Bushra',
                'date': '2025-01-01',  # Past date for archived
                'time': None,
                'url': 'https://www.facebook.com/fpsauofk/videos/1020750989824339/?app=fbl',
                'image': '15.png'
            }
        ]

        for event_data in events_data:
            event = Event(
                title=event_data['title'],
                description=event_data['description'],
                presenter=event_data['presenter'],
                event_url=event_data['url'],
                event_date=datetime.strptime(event_data['date'], '%Y-%m-%d').date(),
                event_time=datetime.strptime(event_data['time'], '%H:%M').time() if event_data['time'] else None,
                image_url=event_data['image'],
                created_by=1,  # Admin user ID
                is_archived=False  # Will be auto-archived if past date
            )
            db.session.add(event)

        db.session.commit()
        print(f"Successfully added {len(events_data)} events to the database!")

if __name__ == '__main__':
    add_events()
