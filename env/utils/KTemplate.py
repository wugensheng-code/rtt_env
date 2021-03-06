Kconfigfile = """menu "Env config" \n

config SYS_AUTO_UPDATE_PKGS
    bool "Auto update pkgs config"
    default y

config SYS_CREATE_MDK_IAR_PROJECT
    bool "Auto create a mdk/iar project"
    default y

if SYS_CREATE_MDK_IAR_PROJECT

    choice
        prompt "Project type"
        help
            Select the project type mdk or iar

        config SYS_CREATE_MDK5
            bool "MDK5"

        config SYS_CREATE_IAR
            bool "IAR"

        config SYS_CREATE_MDK4
            bool "MDK4"
    endchoice

endif

config SYS_PKGS_DOWNLOAD_ACCELERATE
    bool "Use China Mainland server"
    default y

config PROXY_ADDR
    string "Proxy address"

endmenu"""
