#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int inspect_fds(int out_fd) {
    DIR* dir = opendir("/proc/self/fd");
    int dir_fd = dirfd(dir);
    struct dirent* entry;

    while ((entry = readdir(dir))) {
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) {
            continue;
        }

        if (dir_fd == atoi(entry->d_name) || out_fd == atoi(entry->d_name)) {
            continue;
        }

        char target_link_buf[100];
        ssize_t len = readlinkat(dir_fd, entry->d_name, target_link_buf, 100);
        target_link_buf[len] = 0;

        // if (!strcmp(target_link_buf, procdir)) {
        //    continue;
        //}

        dprintf(out_fd, "%s\t%s\n", entry->d_name, target_link_buf);
    }
    close(dir_fd);
    return 0;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: reflector <target_file>\n");
    }
    
    int out_fd = open(argv[1], O_CREAT | O_TRUNC | O_WRONLY, 0644);
    if (out_fd < 0) {
        perror("Error en open");
        return -1;
    }
    inspect_fds(out_fd);

    close(out_fd);
    return 0;
}
