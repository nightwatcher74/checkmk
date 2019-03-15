// test-log.cpp :

#include "pch.h"

#include <filesystem>
#include <string>

#include "cfg.h"

#include "logger.h"
#include "on_start.h"

namespace XLOG {
TEST(LogTest, All) {
    // tests of log:
    // stream OUT
    // e
    using namespace cma::cfg;
    using namespace std;

    // Check Defaults settings on start
    {
        auto& xlogd = XLOG::d;

        auto debug_log_level = cma::cfg::groups::global.debugLogLevel();
        if (debug_log_level < 1)
            EXPECT_TRUE(xlogd.log_param_.directions_ ==
                        xlog::Directions::kDebuggerPrint);
        else
            EXPECT_TRUE(xlogd.log_param_.directions_ ==
                        (xlog::Directions::kDebuggerPrint |
                         xlog::Directions::kFilePrint));

        EXPECT_TRUE(xlogd.type_ == XLOG::LogType::kDebug);
    }

    {
        auto& xlogl = XLOG::l;
        EXPECT_TRUE(
            xlogl.log_param_.directions_ ==
            (xlog::Directions::kDebuggerPrint | xlog::Directions::kFilePrint));
        EXPECT_TRUE(xlogl.type_ == XLOG::LogType::kLog);
    }

    {
        auto& xlogt = XLOG::t;
        EXPECT_TRUE(xlogt.log_param_.directions_ ==
                    (xlog::Directions::kDebuggerPrint));
        EXPECT_TRUE(xlogt.type_ == XLOG::LogType::kTrace);
    }

    {
        auto& xlogstdio = XLOG::stdio;
        EXPECT_TRUE(xlogstdio.log_param_.directions_ ==
                    xlog::Directions::kStdioPrint);
        EXPECT_TRUE(xlogstdio.type_ == XLOG::LogType::kStdio);
    }

    // DEFAULT
    auto prefix = GetDefaultPrefixName();
    std::string prefix_ascii(prefix.begin(), prefix.end());
    auto& lp = l.log_param_;

    EXPECT_TRUE(lp.directions_ & xlog::Directions::kDebuggerPrint);
    EXPECT_TRUE(lp.filename()[0] != 0);

    // Check API
    {
        XLOG::Emitter l(XLOG::LogType::kLog);
        auto& lp = l.log_param_;
        EXPECT_TRUE(lp.directions_ & xlog::Directions::kFilePrint);
        l.configFile(GetCurrentLogFileName());
        EXPECT_TRUE(GetCurrentLogFileName() == lp.filename());
        l.configPrefix(prefix);
        EXPECT_TRUE(prefix == lp.prefix());
        EXPECT_TRUE(prefix_ascii == lp.prefixAscii());
    }

    {
        XLOG::Emitter d(XLOG::LogType::kDebug);
        auto& lp = t.log_param_;
        EXPECT_FALSE(lp.directions_ & xlog::Directions::kFilePrint);
    }

    {
        XLOG::Emitter t(XLOG::LogType::kTrace);
        auto& lp = t.log_param_;
        EXPECT_FALSE(lp.directions_ & xlog::Directions::kFilePrint);

        t.enableFileLog(true);
        EXPECT_TRUE(lp.directions_ & xlog::Directions::kFilePrint);

        t.enableFileLog(false);
        EXPECT_FALSE(lp.directions_ & xlog::Directions::kFilePrint);
    }

    EXPECT_TRUE(lp.directions_ & xlog::Directions::kDebuggerPrint);

    // CLEAN FILE
    {
        XLOG::Emitter l(XLOG::LogType::kLog);
        auto& lp = l.log_param_;
        l.configFile("");
        EXPECT_TRUE(lp.filename()[0] == 0) << "File not changed";
        EXPECT_TRUE(lp.directions_ & xlog::Directions::kFilePrint)
            << "Flag was changed";
        EXPECT_TRUE(lp.directions_ & xlog::Directions::kDebuggerPrint)
            << "Flag was changed";

        l.configPrefix(L"ac");
        std::string new_prefix = lp.prefixAscii();
        EXPECT_TRUE(new_prefix == "ac");
    }

    // *************************************************************
    // *************************************************************
    // *************************************************************
    // *************************************************************

    // DEFAULT CONFIG
    std::string fname = "a";
    setup::ChangeLogFileName(fname);
    EXPECT_EQ(fname, XLOG::l.getLogParam().filename());
    EXPECT_EQ(fname, XLOG::d.getLogParam().filename());
    EXPECT_EQ(fname, XLOG::t.getLogParam().filename());
    EXPECT_EQ(std::string(""), XLOG::stdio.getLogParam().filename());

    setup::EnableDebugLog(true);
    EXPECT_TRUE(XLOG::d.getLogParam().directions_ & xlog::kFilePrint);
    setup::EnableDebugLog(false);
    EXPECT_FALSE(XLOG::d.getLogParam().directions_ & xlog::kFilePrint);

    setup::EnableWinDbg(false);
    EXPECT_FALSE(XLOG::l.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_FALSE(XLOG::d.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_FALSE(XLOG::t.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_FALSE(XLOG::stdio.getLogParam().directions_ & xlog::kDebuggerPrint);

    setup::EnableWinDbg(true);
    EXPECT_TRUE(XLOG::l.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_TRUE(XLOG::d.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_TRUE(XLOG::t.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_FALSE(XLOG::stdio.getLogParam().directions_ & xlog::kDebuggerPrint);

    setup::ReConfigure();
    EXPECT_EQ(XLOG::l.getLogParam().filename(), GetCurrentLogFileName());
    EXPECT_EQ(XLOG::d.getLogParam().filename(), GetCurrentLogFileName());
    EXPECT_EQ(XLOG::t.getLogParam().filename(), GetCurrentLogFileName());
    EXPECT_EQ(XLOG::stdio.getLogParam().filename(), std::string(""));

    EXPECT_TRUE(XLOG::l.getLogParam().directions_ & xlog::kFilePrint);
    EXPECT_TRUE(XLOG::d.getLogParam().directions_ & xlog::kFilePrint)
        << "check debug=yes in cfg";
    EXPECT_FALSE(XLOG::t.getLogParam().directions_ & xlog::kFilePrint)
        << "check debug=yes in cfg";
    EXPECT_FALSE(XLOG::stdio.getLogParam().directions_ & xlog::kFilePrint);

    EXPECT_TRUE(XLOG::l.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_TRUE(XLOG::d.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_TRUE(XLOG::t.getLogParam().directions_ & xlog::kDebuggerPrint);
    EXPECT_FALSE(XLOG::stdio.getLogParam().directions_ & xlog::kDebuggerPrint);

    EXPECT_FALSE(XLOG::l.getLogParam().directions_ & xlog::kEventPrint);
    EXPECT_FALSE(XLOG::d.getLogParam().directions_ & xlog::kEventPrint);
    EXPECT_FALSE(XLOG::t.getLogParam().directions_ & xlog::kEventPrint);
    EXPECT_FALSE(XLOG::stdio.getLogParam().directions_ & xlog::kEventPrint);

    // Output to log
    XLOG::l() << L"This streamed Log Entry and"  // body
                                                 // .....
              << " this is extension 1"          // body
              << '\n';                           // finish
                                                 // Variant two
    XLOG::l() << L"This streamed Log Entry and"  // body
                                                 // .....
              << " this is extension 2"          // body
        ;                                        // finish

    // Variant THREE AND BASIC
    XLOG::l(XLOG::kDrop, "This is dropped a l log {} {}", string("x"), 24);
    if (0) {
        XLOG::l(XLOG::kBp, "This is breakpoint {} {}", string("x"), 24);
    }

    XLOG::d(XLOG::kForce | XLOG::kFile, "This is a forced d log {} {}",
            std::string("x"), 24);

    // Example of debug tracing. In release this output disappears
    XLOG::d("This is a standard debug out {} {}", string("x"), 24);

    // Example of logging. This output exists in release!
    XLOG::l("This is a standard LOG out {} {}", string("x"), 24);
    XLOG::l() << "This is ALSO a standard LOG out" << string(" x ") << 24;

    XLOG::stdio() << XLOG::d("This is stdio write {} {}", string("x"), 24)
                  << '\n';  // you need this usually to have caret return

    XLOG::stdio("This is stdio write TOO {} {}", string("x"),
                24);  // you need this usually to have caret return

    // *************************************************************
    // *************************************************************
    // *************************************************************
    // *************************************************************
}

TEST(LogTest, Setup) {
    using namespace xlog;
    using namespace XLOG;
    auto a_file = "a.log";
    setup::ChangeLogFileName(a_file);
    auto fname = std::string(l.getLogParam().filename());
    EXPECT_TRUE(fname == a_file);

    setup::EnableDebugLog(true);
    EXPECT_TRUE((d.getLogParam().directions_ & Directions::kFilePrint) != 0);

    fname = std::string(d.getLogParam().filename());
    EXPECT_TRUE(fname == a_file);

    setup::EnableDebugLog(false);
    EXPECT_TRUE((d.getLogParam().directions_ & Directions::kFilePrint) == 0);

    setup::EnableWinDbg(false);
    EXPECT_EQ(l.getLogParam().directions_ & Directions::kDebuggerPrint, 0);
    EXPECT_EQ(d.getLogParam().directions_ & Directions::kDebuggerPrint, 0);
    EXPECT_EQ(t.getLogParam().directions_ & Directions::kDebuggerPrint, 0);

    setup::EnableWinDbg(true);
    EXPECT_TRUE((d.getLogParam().directions_ & Directions::kDebuggerPrint) !=
                0);
}

std::string return_current_time_and_date() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);

    std::stringstream ss;
    ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %X");
    return ss.str();
}

TEST(LogTest, EventTest) {
    if (0) {
        // #TODO place in docu
        // how to use windows event log
        XLOG::details::LogWindowsEventCritical(1, "Test is on {}", "error!");
        XLOG::l(XLOG::kCritError) << "Streamed test output kCritError";
        XLOG::l(XLOG::kEvent) << "Streamed test output kEvent";
    }
}

TEST(LogTest, Yaml) {
    namespace fs = std::filesystem;
    using namespace xlog;
    using namespace XLOG;
    std::string log_file_name = "test_file.log";
    fs::path logf = log_file_name;
    fs::remove(logf);

    cma::OnStart(cma::StartTypes::kTest);
    setup::ChangeLogFileName(logf.u8string());

    XLOG::l("simple test");
    XLOG::l(kCritError)("<GTEST> std test {}", 5);
    XLOG::l(kCritError) << "<GTEST> stream test";

    XLOG::l.t() << " trace";
    XLOG::l.w() << " warn";
    XLOG::l.e() << " error";
    XLOG::l.i() << " info";

    XLOG::l.crit("<GTEST> This is critical ptr is {} code is {}", nullptr, 5);
    std::error_code ec;
    EXPECT_TRUE(fs::exists(logf, ec));  // check that file is exists

    {
        std::ifstream in(logf.c_str());
        std::stringstream sstr;
        sstr << in.rdbuf();
        auto contents = sstr.str();
        auto n = std::count(contents.begin(), contents.end(), '\n');
        auto result = cma::tools::SplitString(contents, "\n");
        ASSERT_EQ(result.size(), 8);
        const int start_position = 24;
        EXPECT_NE(std::string::npos, result[0].find("simple test"));
        EXPECT_NE(std::string::npos, result[1].find("<GTEST> std test"));
        EXPECT_NE(std::string::npos, result[2].find("<GTEST> stream test"));
        EXPECT_NE(std::string::npos, result[2].find("[ERROR:CRITICAL]"));

        EXPECT_EQ(start_position, result[3].find("[Trace]  trace"));
        EXPECT_EQ(start_position, result[4].find("[Warn ]  warn"));
        EXPECT_EQ(start_position, result[5].find("[Err  ]  error"));
        EXPECT_EQ(start_position, result[6].find(" info"));
        EXPECT_EQ(
            start_position,
            result[7].find(
                "[ERROR:CRITICAL] <GTEST> This is critical ptr is 0x0 code is 5"));
    }
    fs::remove(logf);
}

}  // namespace XLOG

// Do formatting:
namespace fmt {
TEST(LogTest, Fmt) {
    auto result = formatv("-{} {}-", 3, "c");
    EXPECT_EQ(result, "-3 c-");

    EXPECT_NO_THROW(formatv("<GTEST> -{} {}-", 3));
}
}  // namespace fmt
