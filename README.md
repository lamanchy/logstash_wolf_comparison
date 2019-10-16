# Replacing Logstash with a better alternative

Ondřej Lomič

## abstract

Focus of this work is to find a better alternative for tool Logstash, which became insufficient in Y Soft log processing pipeline. There is a quick Logstash's overview at the beginning of this work, followed by specification of required properties. Throughout overview of existing alternatives is provided as well as reasons whether to implement custom solution.

Because implementation of custom solution was selected as best current alternative, next part of this thesis describes design choices as well as implemented features etc. Finally, a comparison of Logstash and implemented solution is provided, focusing on both functional and non-functional requirements.    

## introduction

- Y Soft and its log processing pipeline
- general overview of what kinds of problems Logstash caused
- "there is no better alternative", therefore custom solution
- design choices and features of wolf
- verify successful replacement by benchmarks, as well as easy of use etc

Quick overview of Logstash follows, furthermore this work is divided into three main parts. The first part focuses on selection of Logstash's replacement, tightly coupled with specification of required properties. The second part describes implementation of custom Logstash replacement, Wolf. Finally, detailed comparison of Wolf and Logstash is provided.

### Logstash overview

- Bit of history
- language JRuby
- usage, part of ELK stack
- actively developed
- loads of plugins
- hw requirements (our case)
- hello world of pipeline configuration

## choosing logstash alternative

- where is logstash used
- rough overview of unsatisfied requirements
- follows: detailed requirements, existing tools vs custom solution

### current requirements

- collection vs server pipeline requirements
- common requirements
- one tool better than two
    - interchangeability of configurations
    - one tool to manage / update

#### collection requirements

- less cpu usage
- less memory usage
- less installation size
- disk queue
- basic filtering, data manipulation
- tcp input, kafka and tcp output

#### server processing requirements

- less cpu usage (more effective processing)
- (therefore) bigger throughput
- effective regex parsing
- easier configuration of more advanced pipelines

### comparison of found alternatives

- viz [here](https://wiki.ysoft.local/display/RSP/1.+Why+to+replace+Logstash+with+our+own+implementation)

### Consequences of implementing custom solution

- it will do exactly what we want to
- it will take time to implement and manage
    - well, that's a big disadvantage

## Wolf implementation

- closely inspired by Logstash
- main differences
    - cpp vs jruby
    - "compiled" vs "interpreted" pipeline
        - easy wolf build will be necessary
- follows
    - design choices, features, build

### design choices?

### features

### build

#### windows docker + windows wsl docker

## comparison of Wolf and Logstash

### functional requirements

### non functional requirements

### comparison on real environment

- only little stack

## conclusion

- wolf holds requirements well
- wolf is much more effective
- wolf is equally bad to debug
- packages and dependencies are quite hell (that's cpp general, not wolf specific)
    - maybe C# could be better, not much slower, much better to work with
- Wolf replaced Logstash completely in Y Soft -> success