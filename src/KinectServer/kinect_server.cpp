/****************************************************************************
*                                                                           *
*  Kinect Server	                                                    *
*  		     			                                    *
*  Author: Roman Gerhat                                                     *
*  Department of Cybernetics, University of West Bohemia, 2012              *
*   			                                                    *
*  Based on Websocketpp.hpp and OpenNI/NiSimpleSkeleton                     *
*       								    *
*  This program reads the user data from Microsoft Kinact via OpenNI        *
*  Skeleton Tracking, stores the recent data of all found users and         *
*  allow sending this information to other connected machines through       *
*  websockets using YAML object serialization.                              *
*  The binary has to have SamplesConfig.xml in the same directory for       *
*  the desired function of Skeleton Tracking			            *
*                                                                           *
****************************************************************************/
//---------------------------------------------------------------------------
// Includes
//---------------------------------------------------------------------------
#include "websocketpp.hpp"

#include <cstring>
#include "unistd.h"
#include <iomanip>
#include <iostream>
#include <sstream>
#include <queue>
#include <vector>
#include <map> 
#include <fstream>    

#include <stdio.h>

#include <XnOpenNI.h>
#include <XnCodecIDs.h>
#include <XnCppWrapper.h>
#include <XnPropNames.h>  
/*#include <cv.h>
#include <highgui.h>               */

#include <boost/archive/iterators/base64_from_binary.hpp>
#include <boost/archive/iterators/insert_linebreaks.hpp>
#include <boost/archive/iterators/transform_width.hpp>
#include <boost/archive/iterators/ostream_iterator.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/bind.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/thread.hpp>
#include <boost/thread/once.hpp>
#include <boost/thread/locks.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/condition.hpp>

using namespace std;

using namespace boost::archive::iterators;

using websocketpp::server;

//---------------------------------------------------------------------------
// Defines
//---------------------------------------------------------------------------
#define SAMPLE_XML_PATH "../../../../Data/SamplesConfig.xml"
#define SAMPLE_XML_PATH_LOCAL "SamplesConfig.xml"
#define MAX_NUM_USERS 15


typedef boost::shared_mutex Lock;
typedef boost::unique_lock< Lock > WriteLock; 
typedef boost::shared_lock< Lock > ReadLock;

typedef map<string, double> Coords;
typedef map<string, Coords> SkeletonMap;

//---------------------------------------------------------------------------
// Globals
//---------------------------------------------------------------------------
xn::Context g_Context;
xn::ScriptNode g_scriptNode;
xn::DepthGenerator g_depth;      
xn::ImageGenerator g_image;                        
xn::DepthMetaData g_depthMD;
xn::ImageMetaData g_imageMD;
xn::UserGenerator g_UserGenerator;
XnBool g_bNeedPose = FALSE;
XnChar g_strPose[20] = "";

boost::once_flag once = BOOST_ONCE_INIT;
boost::shared_mutex _access;
Lock myLock;

// Wanted info
const XnDepthPixel* pDepthMap;
const XnRGB24Pixel* pPixelMap;    
const XnRGB24Pixel* pPixelPoint;

int UsersCount;
SkeletonMap Skeletons[MAX_NUM_USERS];

//---------------------------------------------------------------------------
// Server
//---------------------------------------------------------------------------

class KinectServer : public server::handler {
public:
    std::string getImageData() {
		{
			ReadLock r_lock(myLock);
			stringstream emitter;
			emitter << "[";
			for(int i = 0; i < UsersCount; i++) {
				if (i==0){
					emitter << "{";
				} else {
					emitter << ", {";
				}
				SkeletonMap::iterator joint;
				for (joint = Skeletons[i].begin(); joint != Skeletons[i].end(); ++joint) {
					emitter << "\"" << joint->first << "\": {";
					Coords::iterator pos;
					for (pos = Skeletons[i][joint->first].begin(); pos != Skeletons[i][joint->first].end(); ++pos) {
						emitter << "\"" <<pos->first << "\""<< ": " << pos->second;
						if(pos->first=="Z"){
							emitter << "";
						}
						else{
							emitter << ", ";
						}					
					}
					if(joint->first=="Torso"){
						emitter << "}";
					}
					else{
						emitter << "}, ";
					}
				}
				emitter << "}";	
			}
			emitter << "]";
			return emitter.str();
		}
    }
    
    std::string getDepthMap(bool br) {
	       {
            ReadLock r_lock(myLock);      
      			stringstream emitter;
      			emitter << "{DepthMap," << g_depthMD.XRes() << ","<< g_depthMD.YRes() << "}[";
            
            if(g_depthMD.XRes() != 0){
               for(int i = 0; i < g_depthMD.XRes(); i++) {    
                  if(i>0 && br == true) emitter << "<BR>"; 
                  for(int j = 0; j < g_depthMD.YRes(); j++) {
                     emitter << g_depthMD(i, j);     
                     emitter << ","; 
                  }      
               }
            }  
            emitter << "]";
            return emitter.str();
        }
    }
    
    std::string saveDepthMap() {
	       {            
            ofstream myfile;
            myfile.open ("depthimage.txt");
            myfile << getDepthMap(false);
            myfile.close();
            
            return "depth image saved";
        }
    }

    /**
     * return RGB Image 
     */
    std::string getRGBImage(bool br) {
	       {
            ReadLock r_lock(myLock);
            stringstream emitter;
      	    emitter << "{RGBMap," << g_imageMD.XRes() << ","<< g_imageMD.YRes() << "}[";
            
            for(int i = 0; i < g_imageMD.XRes(); i++) {    
                  if(i>0 && br == true) emitter << "<BR>"; 
                  for(int j = 0; j < g_imageMD.YRes(); j++, pPixelPoint++) {
                       emitter << (int)(pPixelPoint->nRed) << ",";     
                       emitter << (int)(pPixelPoint->nGreen) << ",";
                       emitter << (int)(pPixelPoint->nBlue) << ";"; 
                  }      
            }
            
            emitter << "]";
            return emitter.str();      
        }
    }

    /**
     * saves RGB Image 
     */
    std::string saveRGBImage() {
	       {            
            ofstream myfile;
            myfile.open ("rgbimage.txt");
            myfile << getRGBImage(false);
            myfile.close();
            
            return "RGB image saved";
          /*  cv::Mat colorArr[3];
            cv::Mat colorImage;
            const XnRGB24Pixel* pPixel;

            colorArr[0] = cv::Mat(g_imageMD.YRes(),g_imageMD.XRes(),CV_8U);
            colorArr[1] = cv::Mat(g_imageMD.YRes(),g_imageMD.XRes(),CV_8U);
            colorArr[2] = cv::Mat(g_imageMD.YRes(),g_imageMD.XRes(),CV_8U);

            for (int y=0; y<g_imageMD.YRes(); y++)
            {
              pPixel = pPixelPoint;
              uchar* Bptr = colorArr[0].ptr<uchar>(y);
              uchar* Gptr = colorArr[1].ptr<uchar>(y);
              uchar* Rptr = colorArr[2].ptr<uchar>(y);
                      for(int x=0;x<g_imageMD.XRes();++x , ++pPixel)
                      {
                              Bptr[x] = pPixel->nBlue;
                              Gptr[x] = pPixel->nGreen;
                              Rptr[x] = pPixel->nRed;
                      }
              pPixelPoint += g_imageMD.XRes();
            }
            cv::merge(colorArr,3,colorImage);
        
            std::string str_aux = "CapturedFrames/image_RGB_test.jpg";
            IplImage bgrIpl = colorImage;                      
            cvSaveImage(str_aux.c_str(),&bgrIpl);     */           

        }
    }


	
    void on_message(connection_ptr con, message_ptr msg) {
        if(msg->get_payload()=="skeleton") {
            con->send(getImageData(),msg->get_opcode());
        } else if(msg->get_payload()=="depth") {
            con->send(getDepthMap(true),msg->get_opcode());
        } else if(msg->get_payload()=="rgb") {
            con->send(getRGBImage(true),msg->get_opcode());
        } else if(msg->get_payload()=="savergb") {
            con->send(saveRGBImage(),msg->get_opcode());
        } else if(msg->get_payload()=="savedepth") {
            con->send(saveDepthMap(),msg->get_opcode());
        } else {
            con->send("Unknown client request",msg->get_opcode());
        }
    }
//private:
//	boost::mutex mutex;
};

//---------------------------------------------------------------------------
// OPENNI Methods
//---------------------------------------------------------------------------

XnBool fileExists(const char *fn)
{
	XnBool exists;
	xnOSDoesFileExist(fn, &exists);
	return exists;
}

// Callback: New user was detected
void XN_CALLBACK_TYPE User_NewUser(xn::UserGenerator& generator, XnUserID nId, void* pCookie)
{
    XnUInt32 epochTime = 0;
    xnOSGetEpochTime(&epochTime);
    UsersCount = UsersCount + 1;
    printf("%d New User %d\n", epochTime, nId);
    // New user found
    if (g_bNeedPose)
    {
        g_UserGenerator.GetPoseDetectionCap().StartPoseDetection(g_strPose, nId);
    }
    else
    {
        g_UserGenerator.GetSkeletonCap().RequestCalibration(nId, TRUE);
    }
}
// Callback: An existing user was lost
void XN_CALLBACK_TYPE User_LostUser(xn::UserGenerator& generator, XnUserID nId, void* pCookie)
{
    XnUInt32 epochTime = 0;
    xnOSGetEpochTime(&epochTime);
    UsersCount = UsersCount - 1;
    printf("%d Lost user %d\n", epochTime, nId);	
}
// Callback: Detected a pose
void XN_CALLBACK_TYPE UserPose_PoseDetected(xn::PoseDetectionCapability& capability, const XnChar* strPose, XnUserID nId, void* pCookie)
{
    XnUInt32 epochTime = 0;
    xnOSGetEpochTime(&epochTime);
    printf("%d Pose %s detected for user %d\n", epochTime, strPose, nId);
    g_UserGenerator.GetPoseDetectionCap().StopPoseDetection(nId);
    g_UserGenerator.GetSkeletonCap().RequestCalibration(nId, TRUE);
}
// Callback: Started calibration
void XN_CALLBACK_TYPE UserCalibration_CalibrationStart(xn::SkeletonCapability& capability, XnUserID nId, void* pCookie)
{
    XnUInt32 epochTime = 0;
    xnOSGetEpochTime(&epochTime);
    printf("%d Calibration started for user %d\n", epochTime, nId);
}

void XN_CALLBACK_TYPE UserCalibration_CalibrationComplete(xn::SkeletonCapability& capability, XnUserID nId, XnCalibrationStatus eStatus, void* pCookie)
{
    XnUInt32 epochTime = 0;
    xnOSGetEpochTime(&epochTime);
    if (eStatus == XN_CALIBRATION_STATUS_OK)
    {
        // Calibration succeeded
        printf("%d Calibration complete, start tracking user %d\n", epochTime, nId);		
        g_UserGenerator.GetSkeletonCap().StartTracking(nId);
    }
    else
    {
        // Calibration failed
        printf("%d Calibration failed for user %d\n", epochTime, nId);
        if(eStatus==XN_CALIBRATION_STATUS_MANUAL_ABORT)
        {
            printf("Manual abort occured, stop attempting to calibrate!");
            //return;
        }
        if (g_bNeedPose)
        {
            g_UserGenerator.GetPoseDetectionCap().StartPoseDetection(g_strPose, nId);
        }
        else
        {
            g_UserGenerator.GetSkeletonCap().RequestCalibration(nId, TRUE);
        }
    }
}

#define CHECK_RC(nRetVal, what)					    \
    if (nRetVal != XN_STATUS_OK)				    \
{								    \
    printf("%s failed: %s\n", what, xnGetStatusString(nRetVal));    \
}

//---------------------------------------------------------------------------
// Starting kinect loop with User Tracking
//---------------------------------------------------------------------------

void start_kinect() {
    XnStatus nRetVal = XN_STATUS_OK;
    xn::EnumerationErrors errors;
    UsersCount = 0;

    const char *fn = NULL;
    if    (fileExists(SAMPLE_XML_PATH)) fn = SAMPLE_XML_PATH;
    else if (fileExists(SAMPLE_XML_PATH_LOCAL)) fn = SAMPLE_XML_PATH_LOCAL;
    else {
        printf("Could not find '%s' nor '%s'. Aborting.\n" , SAMPLE_XML_PATH, SAMPLE_XML_PATH_LOCAL);
        //return XN_STATUS_ERROR;
    }
    printf("Reading config from: '%s'\n", fn);

    nRetVal = g_Context.InitFromXmlFile(fn, g_scriptNode, &errors);
    if (nRetVal == XN_STATUS_NO_NODE_PRESENT)
    {
        XnChar strError[1024];
        errors.ToString(strError, 1024);
        printf("%s\n", strError);
        //return (nRetVal);
    }
    else if (nRetVal != XN_STATUS_OK)
    {
        printf("Open failed: %s\n", xnGetStatusString(nRetVal));
        //return (nRetVal);
    }

    nRetVal = g_Context.FindExistingNode(XN_NODE_TYPE_DEPTH, g_depth);      
    CHECK_RC(nRetVal,"No depth");
    
	  nRetVal = g_Context.FindExistingNode(XN_NODE_TYPE_IMAGE, g_image);      
    CHECK_RC(nRetVal,"No image");

    nRetVal = g_Context.FindExistingNode(XN_NODE_TYPE_USER, g_UserGenerator);
    if (nRetVal != XN_STATUS_OK)
    {
        nRetVal = g_UserGenerator.Create(g_Context);
        CHECK_RC(nRetVal, "Find user generator");
    }

    XnCallbackHandle hUserCallbacks, hCalibrationStart, hCalibrationComplete, hPoseDetected;
    if (!g_UserGenerator.IsCapabilitySupported(XN_CAPABILITY_SKELETON))
    {
        printf("Supplied user generator doesn't support skeleton\n");
        //return 1;
    }
    nRetVal = g_UserGenerator.RegisterUserCallbacks(User_NewUser, User_LostUser, NULL, hUserCallbacks);
    CHECK_RC(nRetVal, "Register to user callbacks");
    nRetVal = g_UserGenerator.GetSkeletonCap().RegisterToCalibrationStart(UserCalibration_CalibrationStart, NULL, hCalibrationStart);
    CHECK_RC(nRetVal, "Register to calibration start");
    nRetVal = g_UserGenerator.GetSkeletonCap().RegisterToCalibrationComplete(UserCalibration_CalibrationComplete, NULL, hCalibrationComplete);
    CHECK_RC(nRetVal, "Register to calibration complete");

    if (g_UserGenerator.GetSkeletonCap().NeedPoseForCalibration())
    {
        g_bNeedPose = TRUE;
        if (!g_UserGenerator.IsCapabilitySupported(XN_CAPABILITY_POSE_DETECTION))
        {
            printf("Pose required, but not supported\n");
            //return 1;
        }
        nRetVal = g_UserGenerator.GetPoseDetectionCap().RegisterToPoseDetected(UserPose_PoseDetected, NULL, hPoseDetected);
        CHECK_RC(nRetVal, "Register to Pose Detected");
        g_UserGenerator.GetSkeletonCap().GetCalibrationPose(g_strPose);
    }

    g_UserGenerator.GetSkeletonCap().SetSkeletonProfile(XN_SKEL_PROFILE_ALL);

    nRetVal = g_Context.StartGeneratingAll();
    CHECK_RC(nRetVal, "StartGenerating");

    XnUserID aUsers[MAX_NUM_USERS];
    XnUInt16 nUsers;

    XnSkeletonJointTransformation anyjoint;

    printf("Starting to run\n");
    if(g_bNeedPose)
    {
        printf("Assume calibration pose\n");
    }
    XnUInt32 epochTime = 0;
    while (!xnOSWasKeyboardHit())
    {
        g_Context.WaitOneUpdateAll(g_UserGenerator);
        // print the torso information for the first user already tracking
        nUsers=MAX_NUM_USERS;
        g_UserGenerator.GetUsers(aUsers, nUsers);
        int numTracked=0;
        int userToPrint=-1;

        WriteLock w_lock(myLock);
    	  pDepthMap = g_depth.GetDepthMap();
        pPixelMap = g_image.GetRGB24ImageMap();
            
    	  g_depth.GetMetaData(g_depthMD);    
        g_image.GetMetaData(g_imageMD);
        pPixelPoint = g_imageMD.RGB24Data();


        for(XnUInt16 i=0; i<nUsers; i++) {
    			if(g_UserGenerator.GetSkeletonCap().IsTracking(aUsers[i])==FALSE)
    				continue;
    			{
    				
    				
    				/* Writing all new movements into structure*/
    				/* Head */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_HEAD,anyjoint);
    				Skeletons[i]["Head"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["Head"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["Head"]["Z"] = anyjoint.position.position.Z;
    				/* Neck */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_NECK,anyjoint);
    				Skeletons[i]["Neck"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["Neck"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["Neck"]["Z"] = anyjoint.position.position.Z;
    				/* Left Shoulder */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_LEFT_SHOULDER,anyjoint);
    				Skeletons[i]["LeftShoulder"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["LeftShoulder"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["LeftShoulder"]["Z"] = anyjoint.position.position.Z;
    				/* Right Shoulder */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_RIGHT_SHOULDER,anyjoint);
    				Skeletons[i]["RightShoulder"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["RightShoulder"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["RightShoulder"]["Z"] = anyjoint.position.position.Z;
    				/* Torso */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_TORSO,anyjoint);
    				Skeletons[i]["Torso"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["Torso"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["Torso"]["Z"] = anyjoint.position.position.Z;
    				/* Left Elbow */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_LEFT_ELBOW,anyjoint);
    				Skeletons[i]["LeftElbow"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["LeftElbow"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["LeftElbow"]["Z"] = anyjoint.position.position.Z;
    				/* Right Elbow */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_RIGHT_ELBOW,anyjoint);
    				Skeletons[i]["RightElbow"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["RightElbow"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["RightElbow"]["Z"] = anyjoint.position.position.Z;
    				/* Left Hip */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_LEFT_HIP,anyjoint);
    				Skeletons[i]["LeftHip"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["LeftHip"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["LeftHip"]["Z"] = anyjoint.position.position.Z;
    				/* Right Hip */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_RIGHT_HIP,anyjoint);
    				Skeletons[i]["RightHip"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["RightHip"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["RightHip"]["Z"] = anyjoint.position.position.Z;
    				/* Left Hand */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_LEFT_HAND,anyjoint);
    				Skeletons[i]["LeftHand"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["LeftHand"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["LeftHand"]["Z"] = anyjoint.position.position.Z;
    				/* Right Hand */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_RIGHT_HAND,anyjoint);
    				Skeletons[i]["RightHand"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["RightHand"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["RightHand"]["Z"] = anyjoint.position.position.Z;
    				/* Left Knee */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_LEFT_KNEE,anyjoint);
    				Skeletons[i]["LeftKnee"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["LeftKnee"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["LeftKnee"]["Z"] = anyjoint.position.position.Z;
    				/* Right Knee */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_RIGHT_KNEE,anyjoint);
    				Skeletons[i]["RightKnee"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["RightKnee"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["RightKnee"]["Z"] = anyjoint.position.position.Z;
    				/* Left Foot */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_LEFT_FOOT,anyjoint);
    				Skeletons[i]["LeftFoot"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["LeftFoot"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["LeftFoot"]["Z"] = anyjoint.position.position.Z;
    				/* Right Foot */
    				g_UserGenerator.GetSkeletonCap().GetSkeletonJoint(aUsers[i],XN_SKEL_RIGHT_FOOT,anyjoint);
    				Skeletons[i]["RightFoot"]["X"] = anyjoint.position.position.X;
    				Skeletons[i]["RightFoot"]["Y"] = anyjoint.position.position.Y;
    				Skeletons[i]["RightFoot"]["Z"] = anyjoint.position.position.Z;
    
    				/*printf("user %d: head at (%6.2f,%6.2f,%6.2f)\n",aUsers[i],
                                                                      Skeletons[i]["Head"]["X"],
                                                                      Skeletons[i]["Head"]["Y"],
                                                                      Skeletons[i]["Head"]["Z"]);*/
    			}				
        }
        
    }
    g_scriptNode.Release();
    g_depth.Release();
    g_image.Release();
    g_UserGenerator.Release();
    g_Context.Release();
}

//---------------------------------------------------------------------------
// Kinects thread
//---------------------------------------------------------------------------

void thread_kinect() {
	boost::call_once(start_kinect, once);
}

//---------------------------------------------------------------------------
// Main Program, server start
//---------------------------------------------------------------------------

int main(int argc, char **argv) {
	boost::thread_group threads;
	threads.create_thread(&thread_kinect);
	unsigned short port = 9002;
	if (argc == 2) {
		port = atoi(argv[1]);
        
		if (port == 0) {
			std::cout << "Unable to parse port input " << argv[1] << std::endl;
			return 1;
		}
	}
	try {
		server::handler::ptr h(new KinectServer());
		server echo_endpoint(h);
	
		echo_endpoint.alog().unset_level(websocketpp::log::alevel::ALL);
		echo_endpoint.elog().unset_level(websocketpp::log::elevel::ALL);
	
		echo_endpoint.alog().set_level(websocketpp::log::alevel::CONNECT);
		echo_endpoint.alog().set_level(websocketpp::log::alevel::DISCONNECT);
	
		echo_endpoint.elog().set_level(websocketpp::log::elevel::RERROR);
		echo_endpoint.elog().set_level(websocketpp::log::elevel::FATAL);
	
		std::cout << "Starting WebSocket echo server on port " << port << std::endl;
		echo_endpoint.listen(port);
	} catch (std::exception& e) {
		std::cerr << "Exception: " << e.what() << std::endl;
	}
	threads.join_all();
	return 0;
}
