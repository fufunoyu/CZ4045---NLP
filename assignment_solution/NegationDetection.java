import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations.LemmaAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.stream.Collectors;

public class NegationDetection {

    public static HashSet<String> negationWords = new HashSet<String>();

    public static void changeToNo(int index, List<CoreLabel> list) {
        // System.out.println("In changeToNo");  
        if (index < list.size())
        {
            Boolean replaceChecks = list.get(index).get(TextAnnotation.class).equals("and") 
            || list.get(index).get(TextAnnotation.class).equals("or") 
            || list.get(index).get(TextAnnotation.class).equals(",");

            if (replaceChecks)
            {
                list.get(index).setWord("no1");
                list.get(index).setLemma("no1");
            }
        }
    }

    public static Boolean checkButYet(int index, List<CoreLabel> list) {
        // System.out.println("In checkButYet");
        if (index < list.size())
        {
            if (list.get(index).get(TextAnnotation.class).equals("but") || list.get(index).get(TextAnnotation.class).equals("yet"))
            {
                String wordBefore = list.get(index-1).get(TextAnnotation.class);
                String wordAfter = list.get(index+1).get(TextAnnotation.class);
                System.out.println("But/Yet found between " + wordBefore + " and " + wordAfter);
                return true;
            }
            return false;
        } 
        else 
        {
            return false;
        }
    }

    public static void negateWord(int index, List<CoreLabel> list) {
        // System.out.println("In negateWord");
        if (index < list.size())
        {
            Boolean replaceChecks = !list.get(index).get(TextAnnotation.class).equals("and") 
            && !list.get(index).get(TextAnnotation.class).equals("or") 
            && !list.get(index).get(TextAnnotation.class).equals("no")
            && !list.get(index).get(TextAnnotation.class).equals(",") 
            && !list.get(index).get(TextAnnotation.class).equals(".");

            if (replaceChecks)
            {
                String thisWord = list.get(index).get(TextAnnotation.class);
                String thisLemma = list.get(index).get(LemmaAnnotation.class);
    
                if (!thisWord.startsWith("no"))
                {
                    System.out.println("Replaced " + thisWord);
                    list.get(index).setWord("no1_" + thisWord);
                    list.get(index).setLemma("no1_" + thisLemma);
                }
            }
        }
    }

    public static String appendNo(String word, int index, List<CoreLabel> list) {

        // if (index)
        if (!word.startsWith("no") && !word.startsWith("but"))
        {
            word = "no1_" + word;
        }

        return word;
    }

    public static boolean checkNegation(int index, List<CoreLabel> list) {
        /**
         * Input: Sentence
         * Output: Whether negated 
         */
        
        boolean flag = false;

        // first word can't be negated, skip it 
        if (index == 0) return false;

        // look back previous 3 words 
        String previousWord_1 = list.get(index-1).get(TextAnnotation.class);
        if (NegationDetection.negationWords.contains(previousWord_1))
        {
            flag = true;
        }

        if (index > 1)
        {
            String previousWord_2 = list.get(index-2).get(TextAnnotation.class);
            if (NegationDetection.negationWords.contains(previousWord_2))
            {
                flag = true;
            }
        }

        if (index > 2)
        {
            String previousWord_3 = list.get(index-3).get(TextAnnotation.class);
            if (NegationDetection.negationWords.contains(previousWord_3))
            {
                flag = true;
            }
        }

        // if negation present, process text further
        if (flag == true)
        {
            if (checkButYet(index + 1, list))
            {
                System.out.println("Ending at +1");
                return flag;
            } 
            negateWord(index + 1, list);
            changeToNo(index + 1, list);

            if (checkButYet(index + 2, list))
            {
                System.out.println("Ending at +2");
                return flag;
            }
            negateWord(index + 2, list);
            changeToNo(index + 2, list);

            if (checkButYet(index + 3, list))
            {
                System.out.println("Ending at +3");
                return flag;
            }
            negateWord(index + 3, list);
            changeToNo(index + 3, list);

            if (checkButYet(index + 4, list)) 
            {
                System.out.println("Ending at +4");
                return flag;
            }
            negateWord(index + 4, list);
            changeToNo(index + 4, list);
        }

        return flag;
    }
    public static void main(String[] args) {
        
        // Not-negators
        negationWords.add("no");
        negationWords.add("not");
        negationWords.add("n't");

        // N-negators
        negationWords.add("barely");
        negationWords.add("few");
        negationWords.add("hardly");
        negationWords.add("little");
        negationWords.add("neither");
        negationWords.add("never");
        negationWords.add("nobody");
        negationWords.add("none");
        negationWords.add("nor");
        negationWords.add("nothing");
        negationWords.add("nowhere");
        negationWords.add("rarely");
        negationWords.add("scarcely");
        negationWords.add("seldom");

        String testString = "I'm sure that there is something that says it will not come pictured, but still I was disappointed. The tools helped me get the job done, but they also did not hold up well. The plastic plying tools didn't hold and broke fairly quickly. I can't say that it wasn't user error, but they seemed very cheap.";
        String testStringLower = testString.toLowerCase();
        Properties props = new Properties();
        props.put("annotators", "tokenize, ssplit"); // , pos, lemma");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

        Annotation document = new Annotation(testStringLower);
        pipeline.annotate(document);
        System.out.println("Text processed!");
        
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);
        List<String> wordsOriginal = new ArrayList<>();
        List<String> wordsNegated = new ArrayList<>();

        for (CoreMap sentence : sentences) {

            List<CoreLabel> list = sentence.get(TokensAnnotation.class);

            for (int index = 0; index < list.size(); index++) {

                CoreLabel token = list.get(index);
                String word = token.get(TextAnnotation.class);
                
                System.out.println(word);

                if (index > 0 && checkNegation(index, list))
                {
                    System.out.println("Negating word: " + word);
                    word = appendNo(word, index, list);
                }

                wordsNegated.add(word);
            }
        }
        
        System.out.println("\n\n");

        System.out.println("Original String");
        System.out.println(testString);
        
        System.out.println("New String");
        System.out.println(wordsNegated.toString());
    
    }
}