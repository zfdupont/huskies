package com.huskies.server.districtPlan;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.district.DistrictRepository;
import com.huskies.server.state.StateRepository;
import org.apache.tomcat.util.http.fileupload.IOUtils;
import org.geotools.data.DataUtilities;
import org.geotools.data.FileDataStore;
import org.geotools.data.FileDataStoreFinder;
import org.geotools.data.collection.SpatialIndexFeatureCollection;
import org.geotools.data.simple.SimpleFeatureSource;
import org.geotools.feature.FeatureCollection;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.feature.simple.SimpleFeatureType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

@Service
public class DistrictPlanService {
    @Autowired DistrictPlanRepository districtPlanRepo;
    @Autowired DistrictRepository districtRepo;
    @Autowired
    StateRepository stateRepo;


    // Source: https://javapapers.com/java/glob-with-java-nio/
    private static List<String> match(String glob, Path location) throws IOException {


        List<String> list = new ArrayList<>();

        FileVisitor<Path> matcherVisitor = new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attribs) throws IOException {
                FileSystem fs = FileSystems.getDefault();
                PathMatcher matcher = fs.getPathMatcher(glob);
                if (matcher.matches(file.toAbsolutePath())) {
                    list.add(file.toAbsolutePath().toString());
                }
                return FileVisitResult.CONTINUE;
            }
        };
        Files.walkFileTree(location, matcherVisitor);
        return list;
    }


//    public Map<String, FeatureCollectionPOJO> loadPlansFromJson(){
//        Path relativePath = Paths.get("");
//        String fileGlob = "glob:** /*.zip";
//        Path path = Path.of(relativePath.toAbsolutePath().getParent().toString() + "/data");
//        Map<String, FeatureCollectionPOJO> map = new HashMap<>();
//        try {
//            List<String> files = match(fileGlob, path);
//            List<File> shp_files = new ArrayList<>();
//            files.removeIf(e -> !Pattern.matches(".*\\w{2}\\d{4}.*", e));
//            Path tempDir = Path.of(relativePath.toAbsolutePath().toString() + "/tmp");
//            new File(tempDir.toString()).mkdirs();
//            for(String zip : files){
//                // source: https://stackoverflow.com/questions/15667125/read-content-from-files-which-are-inside-zip-file
//                ZipFile zipFile = new ZipFile(zip);
//                Enumeration<? extends ZipEntry> entries = zipFile.entries();
//                String filename = zip.replaceAll(".* /(.*).zip$", "$1");
//                while(entries.hasMoreElements()){
//                    ZipEntry entry = entries.nextElement();
//                    //check for macosx folder
//                    if(entry.getName().startsWith("__MACOSX")) continue;
//                    InputStream stream = zipFile.getInputStream(entry);
//                    String ext = entry.getName().replaceAll(".*?(.?.?.?.?)?$", "$1");
//                    if(ext.charAt(0) != '.') continue;
//                    File file = new File(String.format("%s/%s%s", tempDir, filename, ext)); file.deleteOnExit();
//                    try(OutputStream outputStream = new FileOutputStream(file)){
//                        IOUtils.copy(stream, outputStream);
//                        if(ext.equals(".shp")) shp_files.add(file);
//                    } catch (Exception e) {
//                        throw new RuntimeException(e);
//                    }
//                }
//            }
//            for(File file : shp_files){
//                map.put(file.getName().replaceAll("(.?.?.?.?)?$", ""), new FeatureCollectionPOJO(loadShapefile(file)));
//            }
//            return map;
//        } catch (Exception e) {
//            throw new RuntimeException(e);
//        }
//    }

    private FeatureCollection<SimpleFeatureType, SimpleFeature> loadShapefile(File file) throws IOException {
        FileDataStore store = FileDataStoreFinder.getDataStore(file);
        // load shape file
        SimpleFeatureSource featureSource = store.getFeatureSource();
        SimpleFeatureSource cachedSource = DataUtilities.source(
                new SpatialIndexFeatureCollection(featureSource.getFeatures()));
        FeatureCollection<SimpleFeatureType, SimpleFeature> collection = cachedSource.getFeatures();
        return collection;
    }

    public void addPrecinctToPlan(String planName, String candidateName, String precinctId, String districtId,
                                     int votes, char party){
        //
    }

    public FeatureCollectionPOJO loadJson(String stateName, String planName) throws IOException {
        Path currentRelativePath = Paths.get("");
        String jsonPath = String.format("%s/scripts/merged%s%s.geojson",
                currentRelativePath.toAbsolutePath(),
                stateName,
                planName);
        byte[] jsonData = Files.readAllBytes(Paths.get(jsonPath));
        ObjectMapper objectMapper = new ObjectMapper();
        FeatureCollectionPOJO f = objectMapper.readValue(jsonData, FeatureCollectionPOJO.class);
        return f;
    }

    public Map<String, Double> getSummary(String planName){
        DistrictPlan plan = districtPlanRepo.findByName(planName).orElseThrow();
        return null;
    }
}
