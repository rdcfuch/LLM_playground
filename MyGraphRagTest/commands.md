### Prep
pip install graphrag
mkdir -p ./ragtest/input


### copy the file to ./ragtest/input


### initial

python3 -m graphrag.index --init --root ./ragtest

### update settings.yaml
update the local LLM and embedding model

### run the index
python3 -m graphrag.index --root ./ragtest


### inference

python3 -m graphrag.query \
--root ./ragtest \
--method global \
"give me a brief of each crusade, each one summarized in 200 words."





# results

## with graphrag: 
The Crusades were a series of religious wars sanctioned by the Roman Catholic Church between the 11th and 13th centuries with the primary objective of recapturing Jerusalem and the Holy Land from Muslim rule. Here is a summary of each crusade, limited to 200 words per summary:

### The First Crusade (1096-1099)
The First Crusade was a response to the appeal by Byzantine Emperor Alexios I Komnenos for Western assistance against the Seljuk Turks who had captured much of the Eastern Roman Empire. Led by Peter the Hermit and Godfrey of Bouillon, the crusaders successfully recaptured Jerusalem from Muslim rule, establishing the Kingdom of Jerusalem.

### The Second Crusade (1147-1149)
The Second Crusade was a response to the capture of Edessa by Zengi. Led by Louis VII of France and Conrad III of Germany, it was largely unsuccessful due to poor leadership, logistical issues, and internal conflicts among the crusaders.

### The Third Crusade (1189-1192)
The Third Crusade was a response to the capture of Jerusalem by Saladin. Led by Richard I of England, Philip II of France, and Frederick Barbarossa of Germany, although they were unable to retake Jerusalem, they did manage to recapture some territories in the Holy Land.

### The Fourth Crusade (1202-1204)
The Fourth Crusade was initially intended to capture Jerusalem but was diverted to Constantinople due to political reasons. The crusaders sacked and looted the city, establishing the Latin Empire in its place.

### The Fifth Crusade (1217-1221)
The Fifth Crusade aimed to recapture Jerusalem from the Ayyubid Sultan Al-Kamil. Despite initial successes, the crusaders were eventually forced to withdraw after a truce was negotiated.

### The Sixth Crusade (1228-1229)
The Sixth Crusade was a brief crusade led by Emperor Frederick II. He negotiated peace with Saladin and was able to briefly reoccupy Jerusalem before leaving.

### The Seventh Crusade (1248-1254)
The Seventh Crusade, also known as the Barons' Crusade, was led by Louis IX of France. Despite initial successes, the crusaders were eventually defeated and forced to retreat.

### The Eighth Crusade (1270)
The Eighth Crusade was a brief crusade led by Louis IX of France. The crusaders were unable to achieve any significant military success and Louis IX died during the campaign.

### The Ninth Crusade (1271-1272)
The Ninth Crusade was a response to the Mongol invasion of the Middle East. The crusaders were able to temporarily halt the Mongols, but were unable to prevent their eventual conquest of much of the region.

### The Children's Crusade (1212)
The Children's Crusade was a failed crusade led by children. The exact details are unclear, but it is believed that thousands of children set out for the Holy Land, many of whom never reached their destination and died along the way.

## without graphrag (which is not accurate)

1. First Crusade (1096-1099): The First Crusade was initiated by Pope Urban II in response to the appeal for help from Byzantine Emperor Alexios I Komnenos. The crusaders, mainly from Western Europe, succeeded in capturing Jerusalem and establishing the Kingdom of Jerusalem.

2. Second Crusade (1147-1149): The Second Crusade was called by Pope Eugenius III to recapture Edessa, which had been lost to the Muslims. The crusade failed to achieve its objective and instead strengthened the Muslim forces under Saladin.

3. Third Crusade (1189-1192): Launched in response to the loss of Jerusalem by the Second Crusade, the Third Crusade was led by three European monarchs: King Richard I of England, King Philip II of France, and Emperor Frederick Barbarossa of the Holy Roman Empire. Despite their successes, they were unable to retake Jerusalem.

4. Seventh Crusade (1248-1254): Led by Louis IX of France, also known as St. Louis, the Seventh Crusade aimed to reclaim the Holy Land by attacking Egypt, the main seat of Muslim power in the Middle East. The crusade was preached by Pope Innocent IV in conjunction with a crusade against Emperor Frederick II and Mongol incursions. However, it also failed to achieve its objective.

5. Albigensian Crusade (1209-1229): Unlike the other Crusades which were directed towards the Holy Land, the Albigensian Crusade was a military campaign launched against the Cathars in Southern France and Languedoc. It was initiated by Pope Innocent III to suppress heresy within Christendom and consolidate the power of the papacy. The crusaders, mostly from Northern France, massacred unarmed civilians during their campaigns.
