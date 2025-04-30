import json
import os
import sys

def create_classical_dataset():
    """Create a comprehensive dataset of classical works with time signatures"""
    
    print("Generating comprehensive classical music dataset...")
    
    # Output dictionary
    output_data = {}
    
    # Add major composers and their works
    add_beethoven(output_data)
    add_mozart(output_data)
    add_bach(output_data)
    add_chopin(output_data)
    add_tchaikovsky(output_data)
    add_brahms(output_data)
    add_haydn(output_data)
    add_schubert(output_data)
    add_debussy(output_data)
    add_ravel(output_data)
    
    # Save the dataset
    output_path = 'classical_time_signatures.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    total_composers = len(output_data)
    total_works = sum(len(works) for works in output_data.values())
    total_movements = sum(sum(len(movements) for movements in composer_works.values()) 
                       for composer_works in output_data.values())
    
    print(f"Dataset generated with:")
    print(f"- {total_composers} composers")
    print(f"- {total_works} musical works")
    print(f"- {total_movements} movements with time signatures")
    print(f"Saved to {output_path}")
    
    return output_data

def add_beethoven(output_data):
    """Add Beethoven's major works"""
    composer = "Ludwig van Beethoven"
    output_data[composer] = {}
    
    # Symphonies
    symphonies = {
        1: {"key": "C major", "nickname": None},
        2: {"key": "D major", "nickname": None},
        3: {"key": "E-flat major", "nickname": "Eroica"},
        4: {"key": "B-flat major", "nickname": None},
        5: {"key": "C minor", "nickname": None},
        6: {"key": "F major", "nickname": "Pastoral"},
        7: {"key": "A major", "nickname": None},
        8: {"key": "F major", "nickname": None},
        9: {"key": "D minor", "nickname": "Choral"}
    }
    
    for num, info in symphonies.items():
        title = f"Symphony No. {num} in {info['key']}"
        if info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Custom movements for each symphony
        if num == 5:
            movements = [
                {"movement": "I. Allegro con brio", "time_signature": "2/4"},
                {"movement": "II. Andante con moto", "time_signature": "3/8"},
                {"movement": "III. Scherzo: Allegro", "time_signature": "3/4"},
                {"movement": "IV. Allegro", "time_signature": "4/4"}
            ]
        elif num == 6:
            movements = [
                {"movement": "I. Awakening of cheerful feelings on arrival in the countryside: Allegro ma non troppo", "time_signature": "2/4"},
                {"movement": "II. Scene by the brook: Andante molto mosso", "time_signature": "12/8"},
                {"movement": "III. Merry gathering of country folk: Allegro", "time_signature": "3/4"},
                {"movement": "IV. Thunderstorm: Allegro", "time_signature": "4/4"},
                {"movement": "V. Shepherd's song. Cheerful and thankful feelings after the storm: Allegretto", "time_signature": "6/8"}
            ]
        elif num == 9:
            movements = [
                {"movement": "I. Allegro ma non troppo, un poco maestoso", "time_signature": "2/4"},
                {"movement": "II. Scherzo: Molto vivace", "time_signature": "3/4"},
                {"movement": "III. Adagio molto e cantabile", "time_signature": "4/4"},
                {"movement": "IV. Finale: Presto - Allegro assai", "time_signature": "4/4"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro con brio", "time_signature": "4/4"},
                {"movement": "II. Andante cantabile con moto", "time_signature": "3/4"},
                {"movement": "III. Menuetto: Allegro molto e vivace", "time_signature": "3/4"},
                {"movement": "IV. Adagio - Allegro molto e vivace", "time_signature": "2/2"}
            ]
        
        output_data[composer][title] = movements
    
    # Piano Sonatas
    sonatas = {
        1: {"key": "F minor", "nickname": None, "opus": "Op. 2 No. 1"},
        8: {"key": "C minor", "nickname": "Pathétique", "opus": "Op. 13"},
        14: {"key": "C-sharp minor", "nickname": "Moonlight", "opus": "Op. 27 No. 2"},
        17: {"key": "D minor", "nickname": "Tempest", "opus": "Op. 31 No. 2"},
        21: {"key": "C major", "nickname": "Waldstein", "opus": "Op. 53"},
        23: {"key": "F minor", "nickname": "Appassionata", "opus": "Op. 57"},
        26: {"key": "E-flat major", "nickname": "Les Adieux", "opus": "Op. 81a"},
        29: {"key": "B-flat major", "nickname": "Hammerklavier", "opus": "Op. 106"},
        32: {"key": "C minor", "nickname": None, "opus": "Op. 111"}
    }
    
    for num, info in sonatas.items():
        title = f"Piano Sonata No. {num} in {info['key']}, {info['opus']}"
        if info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Custom movements for each sonata
        if num == 14:  # Moonlight
            movements = [
                {"movement": "I. Adagio sostenuto", "time_signature": "2/2"},
                {"movement": "II. Allegretto", "time_signature": "3/4"},
                {"movement": "III. Presto agitato", "time_signature": "4/4"}
            ]
        elif num == 8:  # Pathétique
            movements = [
                {"movement": "I. Grave - Allegro di molto e con brio", "time_signature": "4/4"},
                {"movement": "II. Adagio cantabile", "time_signature": "2/4"},
                {"movement": "III. Rondo: Allegro", "time_signature": "2/2"}
            ]
        elif num == 23:  # Appassionata
            movements = [
                {"movement": "I. Allegro assai", "time_signature": "12/8"},
                {"movement": "II. Andante con moto", "time_signature": "3/8"},
                {"movement": "III. Allegro ma non troppo - Presto", "time_signature": "2/2"}
            ]
        elif num == 32:  # Op. 111
            movements = [
                {"movement": "I. Maestoso - Allegro con brio ed appassionato", "time_signature": "12/8"},
                {"movement": "II. Arietta: Adagio molto semplice e cantabile", "time_signature": "9/16"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro", "time_signature": "4/4"},
                {"movement": "II. Adagio", "time_signature": "3/4"},
                {"movement": "III. Rondo: Allegro", "time_signature": "2/4"}
            ]
        
        output_data[composer][title] = movements
    
    # String Quartets
    quartets = {
        1: {"key": "F major", "opus": "Op. 18 No. 1"},
        7: {"key": "F major", "opus": "Op. 59 No. 1", "nickname": "Razumovsky"},
        14: {"key": "C-sharp minor", "opus": "Op. 131"}
    }
    
    for num, info in quartets.items():
        title = f"String Quartet No. {num} in {info['key']}, {info['opus']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        movements = [
            {"movement": "I. Allegro", "time_signature": "4/4"},
            {"movement": "II. Adagio affettuoso ed appassionato", "time_signature": "9/8"},
            {"movement": "III. Scherzo: Allegro molto", "time_signature": "3/4"},
            {"movement": "IV. Allegro", "time_signature": "2/2"}
        ]
        
        output_data[composer][title] = movements
    
    # Piano Concertos
    concertos = {
        4: {"key": "G major", "opus": "Op. 58"},
        5: {"key": "E-flat major", "opus": "Op. 73", "nickname": "Emperor"}
    }
    
    for num, info in concertos.items():
        title = f"Piano Concerto No. {num} in {info['key']}, {info['opus']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        movements = [
            {"movement": "I. Allegro moderato", "time_signature": "4/4"},
            {"movement": "II. Andante con moto", "time_signature": "2/4"},
            {"movement": "III. Rondo: Vivace", "time_signature": "6/8"}
        ]
        
        output_data[composer][title] = movements

def add_mozart(output_data):
    """Add Mozart's major works"""
    composer = "Wolfgang Amadeus Mozart"
    output_data[composer] = {}
    
    # Symphonies
    symphonies = {
        25: {"key": "G minor", "k": "183", "nickname": "Little G minor"},
        29: {"key": "A major", "k": "201", "nickname": None},
        35: {"key": "D major", "k": "385", "nickname": "Haffner"},
        36: {"key": "C major", "k": "425", "nickname": "Linz"},
        38: {"key": "D major", "k": "504", "nickname": "Prague"},
        39: {"key": "E-flat major", "k": "543", "nickname": None},
        40: {"key": "G minor", "k": "550", "nickname": "Great G minor"},
        41: {"key": "C major", "k": "551", "nickname": "Jupiter"}
    }
    
    for num, info in symphonies.items():
        title = f"Symphony No. {num} in {info['key']}, K. {info['k']}"
        if info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Special case for Symphony 40
        if num == 40:
            movements = [
                {"movement": "I. Molto allegro", "time_signature": "2/2"},
                {"movement": "II. Andante", "time_signature": "6/8"},
                {"movement": "III. Menuetto: Allegretto", "time_signature": "3/4"},
                {"movement": "IV. Finale: Allegro assai", "time_signature": "2/2"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro", "time_signature": "4/4"},
                {"movement": "II. Andante", "time_signature": "3/4"},
                {"movement": "III. Menuetto", "time_signature": "3/4"},
                {"movement": "IV. Allegro", "time_signature": "2/2"}
            ]
        
        output_data[composer][title] = movements
    
    # Piano Concertos
    concertos = {
        20: {"key": "D minor", "k": "466"},
        21: {"key": "C major", "k": "467", "nickname": "Elvira Madigan"},
        23: {"key": "A major", "k": "488"},
        24: {"key": "C minor", "k": "491"},
        27: {"key": "B-flat major", "k": "595"}
    }
    
    for num, info in concertos.items():
        title = f"Piano Concerto No. {num} in {info['key']}, K. {info['k']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        movements = [
            {"movement": "I. Allegro", "time_signature": "4/4"},
            {"movement": "II. Andante", "time_signature": "3/4"},
            {"movement": "III. Allegro assai", "time_signature": "6/8"}
        ]
        
        output_data[composer][title] = movements
    
    # Eine kleine Nachtmusik
    output_data[composer]["Serenade No. 13 for strings in G major, K. 525 (\"Eine kleine Nachtmusik\")"] = [
        {"movement": "I. Allegro", "time_signature": "4/4"},
        {"movement": "II. Romanze: Andante", "time_signature": "2/4"},
        {"movement": "III. Menuetto: Allegretto", "time_signature": "3/4"},
        {"movement": "IV. Rondo: Allegro", "time_signature": "2/4"}
    ]
    
    # Requiem
    output_data[composer]["Requiem in D minor, K. 626"] = [
        {"movement": "I. Introitus: Requiem aeternam", "time_signature": "4/4"},
        {"movement": "II. Kyrie eleison", "time_signature": "4/4"},
        {"movement": "III. Sequentia: Dies irae", "time_signature": "4/4"},
        {"movement": "IV. Offertorium: Domine Jesu Christe", "time_signature": "3/4"},
        {"movement": "V. Sanctus", "time_signature": "4/4"},
        {"movement": "VI. Benedictus", "time_signature": "4/4"},
        {"movement": "VII. Agnus Dei", "time_signature": "4/4"},
        {"movement": "VIII. Communio: Lux aeterna", "time_signature": "4/4"}
    ]
    
    # Piano Sonatas
    sonatas = {
        8: {"key": "A minor", "k": "310"},
        11: {"key": "A major", "k": "331", "nickname": "Alla Turca"},
        14: {"key": "C minor", "k": "457"},
        16: {"key": "C major", "k": "545", "nickname": "Sonata facile"}
    }
    
    for num, info in sonatas.items():
        title = f"Piano Sonata No. {num} in {info['key']}, K. {info['k']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Special case for Sonata 11 (Alla Turca)
        if num == 11:
            movements = [
                {"movement": "I. Andante grazioso", "time_signature": "6/8"},
                {"movement": "II. Menuetto", "time_signature": "3/4"},
                {"movement": "III. Alla Turca: Allegretto", "time_signature": "2/4"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro", "time_signature": "4/4"},
                {"movement": "II. Andante", "time_signature": "3/4"},
                {"movement": "III. Allegretto", "time_signature": "2/4"}
            ]
        
        output_data[composer][title] = movements

def add_bach(output_data):
    """Add Bach's major works"""
    composer = "Johann Sebastian Bach"
    output_data[composer] = {}
    
    # Brandenburg Concertos
    for i in range(1, 7):
        keys = ["F major", "F major", "G major", "G major", "D major", "B-flat major"]
        key = keys[i-1]
        
        title = f"Brandenburg Concerto No. {i} in {key}, BWV {1046 + i - 1}"
        
        # Different movements for each concerto
        if i == 3:
            movements = [
                {"movement": "I. (Allegro)", "time_signature": "2/2"},
                {"movement": "II. Adagio", "time_signature": "4/4"},
                {"movement": "III. Allegro", "time_signature": "12/8"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro", "time_signature": "4/4"},
                {"movement": "II. Adagio", "time_signature": "4/4"},
                {"movement": "III. Allegro", "time_signature": "3/8"},
                {"movement": "IV. Menuetto", "time_signature": "3/4"}
            ]
        
        output_data[composer][title] = movements
    
    # The Well-Tempered Clavier (just a few representative pieces)
    wtc_keys = [
        {"key": "C major", "bwv": "846"},
        {"key": "C minor", "bwv": "847"},
        {"key": "D major", "bwv": "850"},
        {"key": "F-sharp major", "bwv": "858"},
        {"key": "B-flat minor", "bwv": "867"}
    ]
    
    for info in wtc_keys:
        title = f"Prelude and Fugue in {info['key']}, BWV {info['bwv']} (WTC Book I)"
        
        movements = [
            {"movement": "Prelude", "time_signature": "4/4"},
            {"movement": "Fugue", "time_signature": "4/4"}
        ]
        
        output_data[composer][title] = movements
    
    # Orchestral Suites
    for i in range(1, 5):
        keys = ["C major", "B minor", "D major", "D major"]
        key = keys[i-1]
        
        title = f"Orchestral Suite No. {i} in {key}, BWV {1066 + i - 1}"
        
        # Suite No. 3 contains Air on the G String
        if i == 3:
            movements = [
                {"movement": "I. Ouverture", "time_signature": "4/4"},
                {"movement": "II. Air (\"Air on the G String\")", "time_signature": "4/4"},
                {"movement": "III. Gavotte", "time_signature": "2/2"},
                {"movement": "IV. Bourrée", "time_signature": "2/2"},
                {"movement": "V. Gigue", "time_signature": "6/8"}
            ]
        else:
            movements = [
                {"movement": "I. Ouverture", "time_signature": "4/4"},
                {"movement": "II. Allemande", "time_signature": "4/4"},
                {"movement": "III. Courante", "time_signature": "3/4"},
                {"movement": "IV. Sarabande", "time_signature": "3/4"},
                {"movement": "V. Menuetto", "time_signature": "3/4"},
                {"movement": "VI. Gigue", "time_signature": "6/8"}
            ]
        
        output_data[composer][title] = movements
    
    # Goldberg Variations
    output_data[composer]["Goldberg Variations, BWV 988"] = [
        {"movement": "Aria", "time_signature": "3/4"},
        {"movement": "Variation 1", "time_signature": "3/4"},
        {"movement": "Variation 2", "time_signature": "2/4"},
        {"movement": "Variation 3: Canone all'Unisono", "time_signature": "12/8"},
        {"movement": "Variation 4", "time_signature": "3/8"},
        {"movement": "Variation 5", "time_signature": "3/4"}
    ]
    
    # Mass in B minor
    output_data[composer]["Mass in B minor, BWV 232"] = [
        {"movement": "I. Kyrie eleison", "time_signature": "4/4"},
        {"movement": "II. Gloria in excelsis Deo", "time_signature": "3/8"},
        {"movement": "III. Credo in unum Deum", "time_signature": "4/4"},
        {"movement": "IV. Sanctus", "time_signature": "4/4"},
        {"movement": "V. Agnus Dei", "time_signature": "4/4"}
    ]

def add_chopin(output_data):
    """Add Chopin's major works"""
    composer = "Frédéric Chopin"
    output_data[composer] = {}
    
    # Nocturnes (a selection)
    nocturnes = {
        1: {"key": "B-flat minor", "opus": "Op. 9 No. 1"},
        2: {"key": "E-flat major", "opus": "Op. 9 No. 2"},
        3: {"key": "B major", "opus": "Op. 9 No. 3"},
        4: {"key": "F major", "opus": "Op. 15 No. 1"},
        5: {"key": "F-sharp major", "opus": "Op. 15 No. 2"},
        8: {"key": "D-flat major", "opus": "Op. 27 No. 2"}
    }
    
    for num, info in nocturnes.items():
        title = f"Nocturne No. {num} in {info['key']}, {info['opus']}"
        
        output_data[composer][title] = [
            {"movement": "Andante", "time_signature": "4/4"}
        ]
    
    # Ballades
    ballades = {
        1: {"key": "G minor", "opus": "Op. 23"},
        2: {"key": "F major", "opus": "Op. 38"},
        3: {"key": "A-flat major", "opus": "Op. 47"},
        4: {"key": "F minor", "opus": "Op. 52"}
    }
    
    for num, info in ballades.items():
        title = f"Ballade No. {num} in {info['key']}, {info['opus']}"
        
        output_data[composer][title] = [
            {"movement": "Largo - Moderato", "time_signature": "6/4"}
        ]
    
    # Piano Sonatas
    sonatas = {
        2: {"key": "B-flat minor", "opus": "Op. 35", "nickname": "Funeral March"},
        3: {"key": "B minor", "opus": "Op. 58"}
    }
    
    for num, info in sonatas.items():
        title = f"Piano Sonata No. {num} in {info['key']}, {info['opus']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        if num == 2:
            movements = [
                {"movement": "I. Grave - Doppio movimento", "time_signature": "4/4"},
                {"movement": "II. Scherzo", "time_signature": "3/4"},
                {"movement": "III. Marche funèbre: Lento", "time_signature": "4/4"},
                {"movement": "IV. Finale: Presto", "time_signature": "2/2"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro maestoso", "time_signature": "4/4"},
                {"movement": "II. Scherzo: Molto vivace", "time_signature": "3/4"},
                {"movement": "III. Largo", "time_signature": "4/4"},
                {"movement": "IV. Finale: Presto non tanto", "time_signature": "6/8"}
            ]
        
        output_data[composer][title] = movements
    
    # Études
    etudes = [
        {"key": "C major", "opus": "Op. 10 No. 1"},
        {"key": "A minor", "opus": "Op. 10 No. 2", "nickname": "Chromatique"},
        {"key": "E major", "opus": "Op. 10 No. 3", "nickname": "Tristesse"},
        {"key": "C-sharp minor", "opus": "Op. 10 No. 4"},
        {"key": "G-flat major", "opus": "Op. 10 No. 5", "nickname": "Black Keys"},
        {"key": "C minor", "opus": "Op. 10 No. 12", "nickname": "Revolutionary"}
    ]
    
    for i, info in enumerate(etudes, 1):
        title = f"Étude in {info['key']}, {info['opus']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        output_data[composer][title] = [
            {"movement": "Allegro", "time_signature": "4/4"}
        ]
    
    # Preludes
    output_data[composer]["24 Preludes, Op. 28"] = [
        {"movement": "No. 1 in C major: Agitato", "time_signature": "4/4"},
        {"movement": "No. 2 in A minor: Lento", "time_signature": "2/2"},
        {"movement": "No. 4 in E minor: Largo", "time_signature": "2/2"},
        {"movement": "No. 6 in B minor: Lento assai", "time_signature": "3/4"},
        {"movement": "No. 7 in A major: Andantino", "time_signature": "3/4"},
        {"movement": "No. 15 in D-flat major: Sostenuto (\"Raindrop\")", "time_signature": "4/4"},
        {"movement": "No. 20 in C minor: Largo", "time_signature": "4/4"}
    ]

def add_tchaikovsky(output_data):
    """Add Tchaikovsky's major works"""
    composer = "Pyotr Ilyich Tchaikovsky"
    output_data[composer] = {}
    
    # Symphonies
    symphonies = {
        1: {"key": "G minor", "opus": "Op. 13", "nickname": "Winter Daydreams"},
        4: {"key": "F minor", "opus": "Op. 36"},
        5: {"key": "E minor", "opus": "Op. 64"},
        6: {"key": "B minor", "opus": "Op. 74", "nickname": "Pathétique"}
    }
    
    for num, info in symphonies.items():
        title = f"Symphony No. {num} in {info['key']}, {info['opus']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Special case for Symphony No. 6
        if num == 6:
            movements = [
                {"movement": "I. Adagio - Allegro non troppo", "time_signature": "4/4"},
                {"movement": "II. Allegro con grazia", "time_signature": "5/4"},
                {"movement": "III. Allegro molto vivace", "time_signature": "2/4"},
                {"movement": "IV. Adagio lamentoso - Andante", "time_signature": "4/4"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro", "time_signature": "4/4"},
                {"movement": "II. Andante", "time_signature": "3/4"},
                {"movement": "III. Scherzo", "time_signature": "3/4"},
                {"movement": "IV. Finale: Allegro", "time_signature": "2/2"}
            ]
        
        output_data[composer][title] = movements
    
    # Ballets
    ballets = {
        "Swan Lake, Op. 20": [
            {"movement": "Introduction", "time_signature": "4/4"},
            {"movement": "Act I No. 2: Valse", "time_signature": "3/4"},
            {"movement": "Act II No. 10: Scene", "time_signature": "4/4"},
            {"movement": "Act II No. 13: Dance of the Swans", "time_signature": "4/4"},
            {"movement": "Act III: Spanish Dance", "time_signature": "3/4"},
            {"movement": "Act IV: Finale", "time_signature": "4/4"}
        ],
        "The Nutcracker, Op. 71": [
            {"movement": "Overture", "time_signature": "2/2"},
            {"movement": "Act I: March", "time_signature": "4/4"},
            {"movement": "Act I: Dance of the Sugar Plum Fairy", "time_signature": "4/4"},
            {"movement": "Act II: Russian Dance (Trepak)", "time_signature": "2/4"},
            {"movement": "Act II: Waltz of the Flowers", "time_signature": "3/4"},
            {"movement": "Act II: Pas de deux", "time_signature": "4/4"}
        ],
        "The Sleeping Beauty, Op. 66": [
            {"movement": "Introduction: La Fée des lilas", "time_signature": "4/4"},
            {"movement": "Act I: Pas d'action", "time_signature": "3/4"},
            {"movement": "Act I: Valse", "time_signature": "3/4"},
            {"movement": "Act III: Pas de quatre", "time_signature": "2/4"},
            {"movement": "Act III: Apothéose", "time_signature": "4/4"}
        ]
    }
    
    for title, movements in ballets.items():
        output_data[composer][title] = movements
    
    # Piano Concerto No. 1
    output_data[composer]["Piano Concerto No. 1 in B-flat minor, Op. 23"] = [
        {"movement": "I. Allegro non troppo e molto maestoso - Allegro con spirito", "time_signature": "4/4"},
        {"movement": "II. Andantino semplice - Prestissimo", "time_signature": "3/4"},
        {"movement": "III. Allegro con fuoco", "time_signature": "3/4"}
    ]
    
    # Violin Concerto
    output_data[composer]["Violin Concerto in D major, Op. 35"] = [
        {"movement": "I. Allegro moderato", "time_signature": "4/4"},
        {"movement": "II. Canzonetta: Andante", "time_signature": "3/4"},
        {"movement": "III. Finale: Allegro vivacissimo", "time_signature": "2/4"}
    ]
    
    # 1812 Overture
    output_data[composer]["1812 Overture, Op. 49"] = [
        {"movement": "Largo - Allegro giusto", "time_signature": "4/4"}
    ]

def add_brahms(output_data):
    """Add Brahms' major works"""
    composer = "Johannes Brahms"
    output_data[composer] = {}
    
    # Symphonies
    symphonies = {
        1: {"key": "C minor", "opus": "Op. 68"},
        2: {"key": "D major", "opus": "Op. 73"},
        3: {"key": "F major", "opus": "Op. 90"},
        4: {"key": "E minor", "opus": "Op. 98"}
    }
    
    for num, info in symphonies.items():
        title = f"Symphony No. {num} in {info['key']}, {info['opus']}"
        
        # Special case for Symphony No. 4
        if num == 4:
            movements = [
                {"movement": "I. Allegro non troppo", "time_signature": "2/2"},
                {"movement": "II. Andante moderato", "time_signature": "6/8"},
                {"movement": "III. Allegro giocoso", "time_signature": "2/4"},
                {"movement": "IV. Allegro energico e passionato (Passacaglia)", "time_signature": "3/4"}
            ]
        else:
            movements = [
                {"movement": "I. Un poco sostenuto - Allegro", "time_signature": "4/4"},
                {"movement": "II. Andante sostenuto", "time_signature": "3/4"},
                {"movement": "III. Un poco allegretto e grazioso", "time_signature": "2/4"},
                {"movement": "IV. Adagio - Più andante - Allegro non troppo, ma con brio", "time_signature": "4/4"}
            ]
        
        output_data[composer][title] = movements
    
    # Piano Concertos
    concertos = {
        1: {"key": "D minor", "opus": "Op. 15"},
        2: {"key": "B-flat major", "opus": "Op. 83"}
    }
    
    for num, info in concertos.items():
        title = f"Piano Concerto No. {num} in {info['key']}, {info['opus']}"
        
        if num == 2:
            movements = [
                {"movement": "I. Allegro non troppo", "time_signature": "4/4"},
                {"movement": "II. Allegro appassionato", "time_signature": "3/4"},
                {"movement": "III. Andante", "time_signature": "2/4"},
                {"movement": "IV. Allegretto grazioso", "time_signature": "2/4"}
            ]
        else:
            movements = [
                {"movement": "I. Maestoso", "time_signature": "4/4"},
                {"movement": "II. Adagio", "time_signature": "3/4"},
                {"movement": "III. Rondo: Allegro non troppo", "time_signature": "6/8"}
            ]
        
        output_data[composer][title] = movements
    
    # Violin Concerto
    output_data[composer]["Violin Concerto in D major, Op. 77"] = [
        {"movement": "I. Allegro non troppo", "time_signature": "4/4"},
        {"movement": "II. Adagio", "time_signature": "3/4"},
        {"movement": "III. Allegro giocoso, ma non troppo vivace", "time_signature": "2/4"}
    ]
    
    # German Requiem
    output_data[composer]["Ein deutsches Requiem (A German Requiem), Op. 45"] = [
        {"movement": "I. Selig sind, die da Leid tragen", "time_signature": "4/4"},
        {"movement": "II. Denn alles Fleisch es ist wie Gras", "time_signature": "3/4"},
        {"movement": "III. Herr, lehre doch mich", "time_signature": "4/4"},
        {"movement": "IV. Wie lieblich sind deine Wohnungen", "time_signature": "3/4"},
        {"movement": "V. Ihr habt nun Traurigkeit", "time_signature": "4/4"},
        {"movement": "VI. Denn wir haben hie keine bleibende Statt", "time_signature": "4/4"},
        {"movement": "VII. Selig sind die Toten", "time_signature": "3/4"}
    ]
    
    # Hungarian Dances
    output_data[composer]["Hungarian Dances, WoO 1"] = [
        {"movement": "No. 1 in G minor: Allegro molto", "time_signature": "2/4"},
        {"movement": "No. 5 in F-sharp minor: Allegro", "time_signature": "2/4"},
        {"movement": "No. 6 in D major: Vivace", "time_signature": "2/4"}
    ]

def add_haydn(output_data):
    """Add Haydn's major works"""
    composer = "Joseph Haydn"
    output_data[composer] = {}
    
    # Symphonies
    symphonies = {
        45: {"key": "F-sharp minor", "nickname": "Farewell"},
        94: {"key": "G major", "nickname": "Surprise"},
        101: {"key": "D major", "nickname": "The Clock"},
        104: {"key": "D major", "nickname": "London"}
    }
    
    for num, info in symphonies.items():
        title = f"Symphony No. {num} in {info['key']}"
        if info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Special case for Symphony No. 94 "Surprise"
        if num == 94:
            movements = [
                {"movement": "I. Adagio cantabile - Vivace assai", "time_signature": "6/8"},
                {"movement": "II. Andante", "time_signature": "2/4"},
                {"movement": "III. Menuetto: Allegro molto", "time_signature": "3/4"},
                {"movement": "IV. Finale: Allegro molto", "time_signature": "2/4"}
            ]
        else:
            movements = [
                {"movement": "I. Adagio - Allegro", "time_signature": "4/4"},
                {"movement": "II. Andante", "time_signature": "3/4"},
                {"movement": "III. Menuetto: Allegretto", "time_signature": "3/4"},
                {"movement": "IV. Finale: Presto", "time_signature": "2/2"}
            ]
        
        output_data[composer][title] = movements
    
    # String Quartets
    quartets = {
        "String Quartet in C major, Op. 76 No. 3 (\"Emperor\")": [
            {"movement": "I. Allegro", "time_signature": "4/4"},
            {"movement": "II. Poco adagio; cantabile", "time_signature": "2/4"},
            {"movement": "III. Menuetto: Allegro", "time_signature": "3/4"},
            {"movement": "IV. Finale: Presto", "time_signature": "2/2"}
        ],
        "String Quartet in D minor, Op. 76 No. 2 (\"Quinten\")": [
            {"movement": "I. Allegro", "time_signature": "4/4"},
            {"movement": "II. Andante o più tosto allegretto", "time_signature": "3/4"},
            {"movement": "III. Menuetto: Allegro ma non troppo", "time_signature": "3/4"},
            {"movement": "IV. Finale: Vivace assai", "time_signature": "2/4"}
        ]
    }
    
    for title, movements in quartets.items():
        output_data[composer][title] = movements
    
    # The Creation
    output_data[composer]["The Creation, Hob. XXI:2"] = [
        {"movement": "Part I: Introduction: The Representation of Chaos", "time_signature": "4/4"},
        {"movement": "Part I: In the beginning God created Heaven and Earth", "time_signature": "4/4"},
        {"movement": "Part II: On mighty pens uplifted soars", "time_signature": "3/4"},
        {"movement": "Part III: In rosy mantle appears", "time_signature": "6/8"}
    ]

def add_schubert(output_data):
    """Add Schubert's major works"""
    composer = "Franz Schubert"
    output_data[composer] = {}
    
    # Symphonies
    symphonies = {
        5: {"key": "B-flat major", "d": "485"},
        8: {"key": "B minor", "d": "759", "nickname": "Unfinished"},
        9: {"key": "C major", "d": "944", "nickname": "Great"}
    }
    
    for num, info in symphonies.items():
        title = f"Symphony No. {num} in {info['key']}, D. {info['d']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        # Special case for Symphony No. 8 "Unfinished"
        if num == 8:
            movements = [
                {"movement": "I. Allegro moderato", "time_signature": "3/4"},
                {"movement": "II. Andante con moto", "time_signature": "3/8"}
            ]
        else:
            movements = [
                {"movement": "I. Allegro", "time_signature": "4/4"},
                {"movement": "II. Andante con moto", "time_signature": "3/4"},
                {"movement": "III. Scherzo: Allegro vivace", "time_signature": "3/4"},
                {"movement": "IV. Allegro vivace", "time_signature": "2/2"}
            ]
        
        output_data[composer][title] = movements
    
    # Piano Sonatas
    sonatas = {
        14: {"key": "A minor", "d": "784"},
        18: {"key": "G major", "d": "894", "nickname": "Fantasie"},
        21: {"key": "B-flat major", "d": "960"}
    }
    
    for num, info in sonatas.items():
        title = f"Piano Sonata No. {num} in {info['key']}, D. {info['d']}"
        if 'nickname' in info and info['nickname']:
            title += f' ("{info["nickname"]}")'
        
        movements = [
            {"movement": "I. Allegro", "time_signature": "4/4"},
            {"movement": "II. Andante", "time_signature": "3/4"},
            {"movement": "III. Scherzo: Allegro vivace", "time_signature": "3/4"},
            {"movement": "IV. Allegro ma non troppo", "time_signature": "2/2"}
        ]
        
        output_data[composer][title] = movements
    
    # Lieder
    lieder = {
        "Erlkönig, D. 328": [
            {"movement": "Erlkönig", "time_signature": "4/4"}
        ],
        "Die Forelle (The Trout), D. 550": [
            {"movement": "Die Forelle", "time_signature": "2/4"}
        ],
        "Gretchen am Spinnrade, D. 118": [
            {"movement": "Gretchen am Spinnrade", "time_signature": "6/8"}
        ],
        "Winterreise, D. 911": [
            {"movement": "No. 1: Gute Nacht", "time_signature": "4/4"},
            {"movement": "No. 5: Der Lindenbaum", "time_signature": "3/4"},
            {"movement": "No. 24: Der Leiermann", "time_signature": "3/4"}
        ]
    }
    
    for title, movements in lieder.items():
        output_data[composer][title] = movements
    
    # Trout Quintet
    output_data[composer]["Piano Quintet in A major, D. 667 (\"Trout\")"] = [
        {"movement": "I. Allegro vivace", "time_signature": "4/4"},
        {"movement": "II. Andante", "time_signature": "3/4"},
        {"movement": "III. Scherzo: Presto", "time_signature": "3/4"},
        {"movement": "IV. Theme and Variations: Andantino", "time_signature": "2/4"},
        {"movement": "V. Finale: Allegro giusto", "time_signature": "6/8"}
    ]

def add_debussy(output_data):
    """Add Debussy's major works"""
    composer = "Claude Debussy"
    output_data[composer] = {}
    
    # Orchestral Works
    orchestral = {
        "Prélude à l'après-midi d'un faune (Prelude to the Afternoon of a Faun), L. 86": [
            {"movement": "Très modéré", "time_signature": "9/8"}
        ],
        "La Mer (The Sea), L. 109": [
            {"movement": "I. De l'aube à midi sur la mer", "time_signature": "6/8"},
            {"movement": "II. Jeux de vagues", "time_signature": "6/8"},
            {"movement": "III. Dialogue du vent et de la mer", "time_signature": "4/4"}
        ],
        "Nocturnes, L. 91": [
            {"movement": "I. Nuages", "time_signature": "6/4"},
            {"movement": "II. Fêtes", "time_signature": "4/4"},
            {"movement": "III. Sirènes", "time_signature": "6/8"}
        ]
    }
    
    for title, movements in orchestral.items():
        output_data[composer][title] = movements
    
    # Piano Works
    piano_suites = {
        "Suite bergamasque, L. 75": [
            {"movement": "I. Prélude", "time_signature": "4/4"},
            {"movement": "II. Menuet", "time_signature": "3/4"},
            {"movement": "III. Clair de lune", "time_signature": "9/8"},
            {"movement": "IV. Passepied", "time_signature": "4/4"}
        ],
        "Préludes, Book 1, L. 117": [
            {"movement": "I. Danseuses de Delphes (Dancers of Delphi)", "time_signature": "3/4"},
            {"movement": "II. Voiles (Sails)", "time_signature": "4/4"},
            {"movement": "III. Le vent dans la plaine (The Wind in the Plain)", "time_signature": "2/4"},
            {"movement": "IV. Les sons et les parfums tournent dans l'air du soir (Sounds and Fragrances Swirl in the Evening Air)", "time_signature": "3/4"},
            {"movement": "VIII. La fille aux cheveux de lin (The Girl with the Flaxen Hair)", "time_signature": "2/4"},
            {"movement": "XII. Minstrels", "time_signature": "2/4"}
        ],
        "Children's Corner, L. 113": [
            {"movement": "I. Doctor Gradus ad Parnassum", "time_signature": "4/4"},
            {"movement": "II. Jimbo's Lullaby", "time_signature": "4/4"},
            {"movement": "III. Serenade for the Doll", "time_signature": "2/4"},
            {"movement": "IV. The Snow is Dancing", "time_signature": "4/4"},
            {"movement": "V. The Little Shepherd", "time_signature": "4/4"},
            {"movement": "VI. Golliwog's Cakewalk", "time_signature": "6/8"}
        ]
    }
    
    for title, movements in piano_suites.items():
        output_data[composer][title] = movements
    
    # Images
    output_data[composer]["Images, Set 1, L. 110"] = [
        {"movement": "I. Reflets dans l'eau (Reflections in the Water)", "time_signature": "4/4"},
        {"movement": "II. Hommage à Rameau (Homage to Rameau)", "time_signature": "3/2"},
        {"movement": "III. Mouvement", "time_signature": "2/4"}
    ]
    
    # Pelléas et Mélisande
    output_data[composer]["Pelléas et Mélisande, L. 88 (opera)"] = [
        {"movement": "Act I, Scene 1: Je ne pourrai plus sortir de cette forêt", "time_signature": "4/4"},
        {"movement": "Act III, Scene 1: Mes longs cheveux descendent", "time_signature": "6/4"},
        {"movement": "Act IV, Scene 4: Maintenant que le père de Pelléas est sauvé", "time_signature": "4/4"}
    ]

def add_ravel(output_data):
    """Add Ravel's major works"""
    composer = "Maurice Ravel"
    output_data[composer] = {}
    
    # Orchestral Works
    orchestral = {
        "Boléro": [
            {"movement": "Tempo di Bolero moderato assai", "time_signature": "3/4"}
        ],
        "Rapsodie espagnole": [
            {"movement": "I. Prélude à la nuit", "time_signature": "2/4"},
            {"movement": "II. Malagueña", "time_signature": "3/4"},
            {"movement": "III. Habanera", "time_signature": "2/4"},
            {"movement": "IV. Feria", "time_signature": "6/8"}
        ],
        "La valse": [
            {"movement": "Poème chorégraphique", "time_signature": "3/4"}
        ],
        "Pavane pour une infante défunte": [
            {"movement": "Lent", "time_signature": "4/4"}
        ]
    }
    
    for title, movements in orchestral.items():
        output_data[composer][title] = movements
    
    # Piano Works
    piano_works = {
        "Jeux d'eau": [
            {"movement": "Jeux d'eau", "time_signature": "4/4"}
        ],
        "Miroirs": [
            {"movement": "I. Noctuelles", "time_signature": "3/4"},
            {"movement": "II. Oiseaux tristes", "time_signature": "2/4"},
            {"movement": "III. Une barque sur l'océan", "time_signature": "6/8"},
            {"movement": "IV. Alborada del gracioso", "time_signature": "6/8"},
            {"movement": "V. La vallée des cloches", "time_signature": "4/4"}
        ],
        "Gaspard de la nuit": [
            {"movement": "I. Ondine", "time_signature": "4/4"},
            {"movement": "II. Le Gibet", "time_signature": "6/4"},
            {"movement": "III. Scarbo", "time_signature": "3/4"}
        ]
    }
    
    for title, movements in piano_works.items():
        output_data[composer][title] = movements
    
    # Chamber Music
    output_data[composer]["String Quartet in F major"] = [
        {"movement": "I. Allegro moderato - Très doux", "time_signature": "4/4"},
        {"movement": "II. Assez vif - Très rythmé", "time_signature": "3/4"},
        {"movement": "III. Très lent", "time_signature": "4/4"},
        {"movement": "IV. Vif et agité", "time_signature": "5/8"}
    ]
    
    # Piano Concertos
    output_data[composer]["Piano Concerto in G major"] = [
        {"movement": "I. Allegramente", "time_signature": "3/4"},
        {"movement": "II. Adagio assai", "time_signature": "3/4"},
        {"movement": "III. Presto", "time_signature": "2/4"}
    ]
    
    output_data[composer]["Piano Concerto for the Left Hand in D major"] = [
        {"movement": "Lento - Allegro - Lento", "time_signature": "4/4"}
    ]
    
    # Daphnis et Chloé
    output_data[composer]["Daphnis et Chloé (ballet)"] = [
        {"movement": "Part I: Introduction et Danse religieuse", "time_signature": "4/4"},
        {"movement": "Part II: Lever du jour", "time_signature": "5/4"},
        {"movement": "Part III: Danse générale", "time_signature": "5/4"}
    ]

def merge_with_existing_data(new_data, existing_path):
    """Merge newly generated data with existing data"""
    print(f"Attempting to merge with existing data at: {existing_path}")
    
    try:
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            print(f"Successfully loaded existing data with {len(existing_data)} composers")
    except Exception as e:
        print(f"Error loading existing data: {str(e)}")
        print("Creating a new dataset instead.")
        existing_data = {}
    
    # Create a merged dataset
    merged_data = existing_data.copy()
    
    # Add new data where it doesn't exist in the original
    for composer, works in new_data.items():
        if composer not in merged_data:
            merged_data[composer] = {}
        
        for work_title, movements in works.items():
            # Skip if work already exists (preserve manual corrections)
            if work_title not in merged_data[composer]:
                merged_data[composer][work_title] = movements
    
    # Save merged data
    output_path = 'expanded_time_signatures.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    # Statistics
    old_composers = len(existing_data)
    old_works = sum(len(works) for works in existing_data.values())
    
    new_composers = len(merged_data) - old_composers
    new_works = sum(len(works) for works in merged_data.values()) - old_works
    
    print(f"Merged data saved to {output_path}")
    print(f"Added {new_composers} new composers and {new_works} new works to the existing dataset.")
    
    return merged_data

def main():
    """Main function to run the script"""
    print("Classical Music Time Signature Dataset Generator")
    print("===============================================")
    print("This script creates a comprehensive dataset of classical music time signatures")
    print("without requiring the music21 library.")
    print("")
    print("Options:")
    print("1: Generate complete classical dataset")
    print("2: Merge with existing dataset")
    
    while True:
        choice = input("Enter your choice (1 or 2): ")
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    if choice == '1':
        # Generate new dataset
        dataset = create_classical_dataset()
        
        # Ask if user wants to merge with existing data
        merge_choice = input("Do you want to merge with existing data? (y/n): ")
        if merge_choice.lower() == 'y':
            existing_path = input("Enter path to existing JSON file: ")
            merge_with_existing_data(dataset, existing_path)
    else:
        # Merge with existing data
        print("Enter path to existing JSON file:")
        existing_path = input("> ")
        
        # Generate new dataset and merge
        dataset = create_classical_dataset()
        merge_with_existing_data(dataset, existing_path)

if __name__ == "__main__":
    main()
