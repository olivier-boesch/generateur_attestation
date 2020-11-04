#!/usr/bin/python3
# coding: utf8
from collections import OrderedDict
from datetime import datetime, timedelta
from fpdf import FPDF
import os.path
from kivy import platform
from kivy.logger import Logger

title = "ATTESTATION DE DÉPLACEMENT DÉROGATOIRE"

prelude = "En application du décret n°2020-1310 du 29 octobre 2020 prescrivant les mesures générales nécessaires pour " \
          "faire face à l'épidémie de Covid19 dans le cadre de l'état d'urgence sanitaire "

debut = u"Je soussigné(e),\n\nMme/M {nom:s} {prenom:s}\n\nné(e) le : {date_naissance:s} à {lieu_naissance:s}\n\nDeumeurant : {" \
        "adresse:s} {code_postal:s} {commune:s}\n\ncertifie que mon déplacement est lié au motif suivant autorisé par " \
        "le décret n°2020-1310 du 29 octobre 2020 prescrivant les mesures générales nécessaires pour faire face à " \
        "l'épidémie de Covid19 dans le cadre de l'état d'urgence sanitaire  : "

motifs = OrderedDict([
        ("Déplacement Domicile-Travail", "Déplacements entre le domicile et le lieu d'exercice de l'activité "
                                         "professionnelle ou un établissement d'enseignement ou de formation, "
                                         "déplacements professionnels ne pouvant être différés , déplacements pour "
                                         "un concours ou un examen. Déplacements pour effectuer des achats de "
                                         "fournitures nécessaires à l'activité professionnelle, des achats de "
                                         "première nécessité  dans des établissements dont les activités demeurent "
                                         "autorisées, le retrait de commande et les livraisons à domicile;"),
        ("Déplacement pour achats", "Déplacements pour effectuer des achats de fournitures nécessaires à l'activité "
                                    "professionnelle, des achats de première nécessité  dans des établissements "
                                    "dont les activités demeurent autorisées, le retrait de commande et les "
                                    "livraisons à domicile;"),
        ("Consultation médicale", "Consultations, examens et soins ne pouvant être assurés à distance et l'achat de "
                                  "médicaments;"),
        ("Motif familial impérieux", "Déplacements pour motif familial impérieux, pour l'assistance aux personnes "
                                     "vulnérables et précaires ou la garde d'enfants;"),
        ("Personne en situtation de handicap", "Déplacement des personnes en situation de handicap et leur "
                                               "accompagnant;"),
        ("Activité physique", "Déplacements brefs, dans la limite d'une heure quotidienne et dans un rayon maximal "
                              "d'un kilomètre autour du domicile, liés soit à l'activité physique individuelle des "
                              "personnes, à l'exclusion de toute pratique sportive collective et de toute proximité "
                              "avec d'autres personnes, soit à la promenade avec les seules personnes regroupées dans "
                              "un même domicile, soit aux besoins des animaux de compagnie;"),
        ("Convocation administrative", "Convocation judiciaire ou administrative et pour se rendre dans un service "
                                       "public;"),
        ("Mission d'intérêt général", "Participation à des missions d'intérêt général sur demande de l'autorité "
                                      "administrative;"),
        ("École et périscolaire", "Déplacement pour chercher les enfants à l'école et à l'occasion de leurs activités "
                                  "périscolaires;")])

fin = "Fait à {commune:s}\n\nle : {date:s} à {heure:s}"

motifs_courts = list(motifs.keys())
motifs_longs = [motifs[k] for k in motifs.keys()]


class PDF(FPDF):
    pass


def generer_pdf(save_dir, data, motif, urgence=False):
    instant = datetime.now()
    Logger.info("Att: Génération le {:s} pour {:s} (urgence : {:s})".format(str(instant), motifs_courts[int(motif)], str(urgence)))
    if urgence:
        try:
            delta = int(data['decalage_help'])
        except ValueError:
            delta = 0
        instant = instant - timedelta(minutes=delta)
    if platform == 'android':
        mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
                'août', 'septembre', 'octobre', 'novembre', 'décembre']
        date = instant.strftime("%d ").lstrip('0')
        date += mois[int(instant.strftime("%m"))-1]
        date += instant.strftime(" %Y")
    else:
        date = instant.strftime("%d %B %Y").lstrip('0')
    data['date'] = date
    heure = instant.strftime("%H:%M")
    data['heure'] = heure
    Logger.info("Att: Generated at {:s} on {:s}".format(heure, date))
    header = debut.format(**data)
    footer = fin.format(**data)
    pdf = PDF(orientation='P', unit="mm", format='A4')
    pdf.set_margins(left=15, top=20, right=13)
    pdf.add_page()
    pdf.set_font(family='Times', style='B', size=20)
    pdf.multi_cell(w=0,h=20,txt=title)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, header)
    pdf.ln()
    for i in range(len(motifs_longs)):
        if i == motif:
            pdf.cell(w=5, h=5, border=1, txt="X")
        else:
            pdf.cell(w=5, h=5, border=1, txt=" ")
        pdf.set_x(30)
        pdf.multi_cell(w=0, h=5, txt=motifs_longs[i])
        pdf.ln()
    pdf.multi_cell(0, 5, footer)
    pdf.ln()
    filename = instant.strftime("attestation-%Y-%m-%d_%H-%M-%S.pdf")
    pdf.output(name=os.path.join(save_dir, filename), dest='F')
    return os.path.join(save_dir, filename)


if __name__ == "__main__":
    print(motifs_courts)
    print(motifs_longs)
    data = {'nom': 'Tims', 'prenom': 'Carl', 'adresse': "pas d'adresse", 'commune': 'Nowhere', 'code_postal': '12345', 'date_naissance': '01/02/2003', 'lieu_naissance': 'truc', 'decalage_help': '20'}
    generer_pdf('.', data, motif=1, urgence=True)


